"""Diagnostyka poczty wychodzącej.

Powstało, bo powiadomienia o zgłoszeniach nie docierały, a jedynym objawem był
wpis w logu na poziomie informacyjnym, łatwy do przeoczenia. Ta komenda mówi
wprost, na czym się zatrzymuje.

    python manage.py check_email
    python manage.py check_email --send adres@example.com

Na Railway uruchamiać z zakładki terminala w panelu usługi, bo to tam ustawione
są zmienne środowiskowe, a nie lokalny plik .env.
"""

from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.core.management.base import BaseCommand


def mask_login(value):
    """Login trzeba rozpoznać, więc zostaje domena, znika część przed małpą."""
    if not value:
        return "PUSTE"
    if "@" in value:
        local_part, domain = value.split("@", 1)
        return f"{local_part[:2]}...@{domain}"
    return f"{value[:2]}... ({len(value)} znaków)"


def mask_password(value):
    """Z hasła nie pokazujemy ani jednego znaku, bo to trafia na ekran i do logów."""
    return f"ustawione ({len(value)} znaków)" if value else "PUSTE"


class Command(BaseCommand):
    help = "Sprawdza konfigurację poczty i połączenie z serwerem SMTP."

    def add_arguments(self, parser):
        parser.add_argument(
            "--send",
            metavar="ADRES",
            help="Wyśle wiadomość testową pod podany adres. Bez tego tylko sprawdza połączenie.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Konfiguracja"))

        backend = settings.EMAIL_BACKEND
        for label, value in [
            ("DEBUG", settings.DEBUG),
            ("EMAIL_BACKEND", backend),
            ("EMAIL_HOST", settings.EMAIL_HOST),
            ("EMAIL_PORT", settings.EMAIL_PORT),
            ("EMAIL_USE_SSL", getattr(settings, "EMAIL_USE_SSL", False)),
            ("EMAIL_HOST_USER", mask_login(settings.EMAIL_HOST_USER)),
            ("EMAIL_HOST_PASSWORD", mask_password(settings.EMAIL_HOST_PASSWORD)),
            ("EMAIL_FROM", settings.EMAIL_FROM),
            ("ADMIN_NOTIFICATION_EMAIL", settings.ADMIN_NOTIFICATION_EMAIL),
        ]:
            self.stdout.write(f"  {label:26} {value}")

        self.stdout.write("")

        if "console" in backend:
            self.stdout.write(self.style.WARNING(
                "Backend konsolowy: maile trafiają na standardowe wyjście, a nie do adresata.\n"
                "Tak ma być lokalnie przy DEBUG=True. Jeśli widzisz to na produkcji, "
                "to znaczy, że DEBUG jest włączone i to jest przyczyna."
            ))
            return

        missing = [
            name for name, value in [
                ("EMAIL_HOST_USER", settings.EMAIL_HOST_USER),
                ("EMAIL_HOST_PASSWORD", settings.EMAIL_HOST_PASSWORD),
            ] if not value
        ]
        if missing:
            self.stdout.write(self.style.ERROR(
                f"Brakuje zmiennych środowiskowych: {', '.join(missing)}.\n"
                "Aplikacja pomija wtedy wysyłkę i zapisuje zgłoszenie wyłącznie w bazie.\n"
                "To najczęstsza przyczyna braku maili po wdrożeniu: plik .env nie trafia "
                "do repozytorium, więc zmienne trzeba ustawić osobno w panelu hostingu."
            ))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Połączenie z serwerem"))
        connection = get_connection(fail_silently=False)
        try:
            connection.open()
        except Exception as error:
            self.stdout.write(self.style.ERROR(f"  Nie udało się połączyć: {error}"))
            self.stdout.write(
                "\n  Typowe przyczyny: błędne hasło (Zoho wymaga hasła aplikacji, "
                "nie hasła do konta),\n"
                "  zły port (465 dla SSL, 587 dla STARTTLS) albo adres nadawcy "
                "nieprzypisany do konta."
            )
            return
        connection.close()
        self.stdout.write(self.style.SUCCESS("  Połączenie i logowanie działają."))

        address = options.get("send")
        if not address:
            self.stdout.write(
                "\nŻeby sprawdzić całą drogę wiadomości, uruchom ponownie z "
                "--send adres@example.com"
            )
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Wiadomość testowa"))
        try:
            send_mail(
                subject="Test poczty, Spektrum Umysłu",
                message=(
                    "Ta wiadomość została wysłana komendą check_email.\n"
                    "Jeśli do Ciebie dotarła, wysyłka powiadomień o zgłoszeniach działa."
                ),
                from_email=settings.EMAIL_FROM,
                recipient_list=[address],
                fail_silently=False,
            )
        except Exception as error:
            self.stdout.write(self.style.ERROR(f"  Wysyłka nie powiodła się: {error}"))
            return

        self.stdout.write(self.style.SUCCESS(f"  Wysłano na {address}."))
        self.stdout.write(
            "  Jeśli wiadomość nie dotrze w ciągu kilku minut, sprawdź folder spam "
            "oraz rekordy SPF i DKIM domeny."
        )
