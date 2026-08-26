"""Widoki serwisu.

Powiadomienia mailowe wychodzą synchronicznie. Wcześniej szły z wątku oznaczonego
jako daemon, a taki wątek jest ubijany bez czekania, gdy proces się kończy.
Na Railway proces gunicorna bywa wymieniany przy wdrożeniu i restarcie, więc
zgłoszenie zapisywało się w bazie, użytkownik widział potwierdzenie, a mail nie
dochodził i nie zostawało po tym żadnego śladu. Wysyłka przez Zoho trwa około
sekundy, a formularz i tak przeładowuje stronę.
"""

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from . import site_data
from .forms import AppointmentForm, DataSubjectRightsForm
from .models import BlogCategory, BlogPost, CookieConsent, DataSubjectRightsRequest

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Poczta
# ─────────────────────────────────────────────────────────────────────

def email_is_configured():
    """Bez danych logowania do SMTP nie ma czym wysłać.

    EMAIL_HOST ma wartość domyślną, więc nie nadaje się na wskaźnik konfiguracji.
    Rozstrzygają login i hasło, których domyślne wartości są puste.
    """
    return bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)


def _notify(admin_subject, admin_body, client_email='', client_subject='', client_body=''):
    """Powiadomienie do gabinetu i opcjonalne potwierdzenie dla klienta.

    Nigdy nie przerywa obsługi zgłoszenia, bo rekord jest już w bazie. Każdy
    adres próbowany osobno, żeby zły adres klienta nie zabrał powiadomienia
    do gabinetu. Każde niepowodzenie ląduje w logu jako błąd, a nie jako
    informacja, żeby było widoczne w panelu Railway.
    """
    if not email_is_configured():
        logger.error(
            'Poczta nieskonfigurowana: EMAIL_HOST_USER lub EMAIL_HOST_PASSWORD '
            'jest puste w środowisku. Powiadomienie NIE zostało wysłane: %s',
            admin_subject,
        )
        return

    outgoing = [(admin_subject, admin_body, settings.ADMIN_NOTIFICATION_EMAIL)]
    if client_email and client_subject:
        outgoing.append((client_subject, client_body, client_email))

    for subject, body, recipient in outgoing:
        try:
            send_mail(subject, body, settings.EMAIL_FROM, [recipient], fail_silently=False)
            logger.info('Wysłano "%s" na %s', subject, recipient)
        except Exception:
            logger.error('Nie udało się wysłać "%s" na %s', subject, recipient, exc_info=True)


def _appointment_subject(raw):
    """Etykieta tematu wybranego w formularzu rezerwacji.

    Nazwy pochodzą z cennika, żeby mail nazywał usługę tak samo jak strona.
    """
    service = site_data.SERVICES.get(raw)
    if service:
        return service['name']
    return 'Inne' if raw == 'inne' else (raw or 'Nie podano')


# ─────────────────────────────────────────────────────────────────────
# Strony statyczne
# ─────────────────────────────────────────────────────────────────────

def home(request):
    return render(request, 'home.html', {'form': AppointmentForm()})


def thanks(request):
    return render(request, 'thanks.html')


def contact(request):
    return render(request, 'contact.html', {'form': AppointmentForm()})


def about_us(request):
    return render(request, 'about_us.html')


def privacy(request):
    return render(request, 'privacy.html')


def cookie_policy(request):
    return render(request, 'cookie_policy.html')


def terms(request):
    return render(request, 'terms.html')


def standardy_ochrony_maloletnich(request):
    """Publikacja Standardów Ochrony Małoletnich jest obowiązkiem ustawowym (art. 22c)."""
    return render(request, 'standardy_ochrony_maloletnich.html')


def pricing(request):
    return render(request, 'pricing.html', {
        'form': AppointmentForm(),
        'faq': site_data.PRICING_FAQ,
        'faq_schema': site_data.faq_schema(site_data.PRICING_FAQ),
    })


# Nazwa widoku/szablonu -> klucz w cenniku (nie zawsze są identyczne).
SERVICE_KEY_TO_PRICE = {
    'diagnoza_adhd': 'adhd',
    'diagnoza_autyzmu': 'autyzm',
    'wsparcie_online': 'online',
    'konsultacje': 'konsultacja',
    'tus': 'tus',
    'terapia_indywidualna': 'terapia',
    'logopedia': 'logopedia',
}


def service_page(request, key):
    """Wszystkie strony usług renderują się tak samo, różni je szablon i zestaw FAQ."""
    return render(request, f'{key}.html', {
        'form': AppointmentForm(),
        'faq': site_data.FAQ[key],
        'faq_schema': site_data.faq_schema(site_data.FAQ[key]),
        'service': site_data.SERVICES[SERVICE_KEY_TO_PRICE[key]],
    })


def lokalizacja(request, slug):
    """Strona gabinetu w danym mieście, /opole/ i /nysa/."""
    loc = next((l for l in site_data.LOCATIONS if l['slug'] == slug), None)
    if loc is None:
        raise Http404
    faq = site_data.LOCATION_FAQ[slug]
    return render(request, 'lokalizacja.html', {
        'loc': loc,
        'faq': faq,
        'faq_schema': site_data.faq_schema(faq),
        'form': AppointmentForm(),
    })


# ─────────────────────────────────────────────────────────────────────
# Formularze
# ─────────────────────────────────────────────────────────────────────

def _appointment_notification(request, appointment):
    subject_label = _appointment_subject(request.POST.get('subject', ''))
    submitted_at = appointment.created_at.strftime('%d.%m.%Y %H:%M')
    return {
        'admin_subject': f'Nowa wizyta: {appointment.name}',
        'admin_body': (
            f'NOWA WIZYTA UMÓWIONA\n\n'
            f'Osoba: {appointment.name}\n'
            f'Telefon: {appointment.phone}\n'
            f'Email: {appointment.email or "nie podano"}\n'
            f'Temat: {subject_label}\n'
            f'Data zgłoszenia: {submitted_at}\n'
            f'Zgoda na przetwarzanie danych: {"tak" if appointment.data_processing_consent else "nie"}\n\n'
            f'Skontaktuj się z klientem w ciągu 24 godzin.'
        ),
        'client_email': appointment.email or '',
        'client_subject': f'Potwierdzenie umówienia wizyty, {site_data.SITE_NAME}',
        'client_body': (
            f'Szanowni Państwo {appointment.name},\n\n'
            f'dziękujemy za umówienie wizyty.\n\n'
            f'Szczegóły zgłoszenia:\n'
            f'Imię i nazwisko: {appointment.name}\n'
            f'Telefon: {appointment.phone}\n'
            f'Email: {appointment.email}\n'
            f'Temat: {subject_label}\n\n'
            f'Skontaktujemy się w ciągu 24 godzin, żeby potwierdzić dokładny termin.\n\n'
            f'W razie pytań prosimy o kontakt:\n'
            f'Telefon: {site_data.PHONE_DISPLAY}\n'
            f'Email: {settings.EMAIL_FROM}\n\n'
            f'Z poważaniem,\n{site_data.SITE_NAME}'
        ),
    }


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def book(request):
    if request.method != 'POST':
        return redirect('home')

    form = AppointmentForm(request.POST)
    if not form.is_valid():
        logger.warning('Formularz rezerwacji odrzucony: %s', form.errors)
        messages.error(request, 'Proszę poprawić błędy w formularzu.')
        return render(request, 'home.html', {'form': form})

    try:
        appointment = form.save()
    except Exception:
        logger.error('Zapis rezerwacji nie powiódł się', exc_info=True)
        messages.error(request, 'Wystąpił błąd podczas zapisywania. Spróbuj ponownie lub zadzwoń.')
        return render(request, 'home.html', {'form': form})

    logger.info('Zapisano wizytę id=%s', appointment.pk)
    _notify(**_appointment_notification(request, appointment))
    messages.success(request, 'Wizyta została umówiona pomyślnie!')
    return redirect('thanks')


@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def data_subject_rights(request):
    if request.method != 'POST':
        return render(request, 'data_subject_rights.html', {'form': DataSubjectRightsForm()})

    form = DataSubjectRightsForm(request.POST)
    if not form.is_valid():
        return render(request, 'data_subject_rights.html', {'form': form})

    data = form.cleaned_data
    rodo_request = DataSubjectRightsRequest.objects.create(
        request_type=data['request_type'],
        full_name=data['full_name'],
        email=data['email'],
        phone=data.get('phone', ''),
        identification=data['identification'],
        details=data.get('details', ''),
        privacy_consent=data['privacy_consent'],
    )
    logger.info('Zapisano żądanie RODO %s', rodo_request.tracking_number)

    _notify(
        admin_subject=f'Nowe żądanie RODO: {rodo_request.tracking_number}',
        admin_body=(
            f'Otrzymano nowe żądanie RODO.\n\n'
            f'Numer: {rodo_request.tracking_number}\n'
            f'Rodzaj: {rodo_request.get_request_type_display()}\n'
            f'Osoba: {rodo_request.full_name}\n'
            f'Email: {rodo_request.email}\n'
            f'Telefon: {rodo_request.phone or "nie podano"}\n\n'
            f'Termin na odpowiedź: 30 dni. Szczegóły w panelu administracyjnym.'
        ),
        client_email=rodo_request.email,
        client_subject=f'Potwierdzenie żądania RODO {rodo_request.tracking_number}',
        client_body=(
            f'Szanowni Państwo,\n\n'
            f'potwierdzamy otrzymanie żądania dotyczącego realizacji praw wynikających z RODO.\n\n'
            f'Numer referencyjny: {rodo_request.tracking_number}\n'
            f'Rodzaj żądania: {rodo_request.get_request_type_display()}\n'
            f'Data złożenia: {rodo_request.created_at:%d.%m.%Y %H:%M}\n\n'
            f'Zgodnie z przepisami RODO udzielimy odpowiedzi w terminie do 30 dni '
            f'od daty otrzymania żądania.\n\n'
            f'Z poważaniem,\n{site_data.SITE_NAME}'
        ),
    )

    messages.success(
        request,
        f'Twoje żądanie zostało złożone pomyślnie. Numer referencyjny: {rodo_request.tracking_number}',
    )
    return render(request, 'data_subject_rights.html', {
        'success': True,
        'tracking_number': rodo_request.tracking_number,
    })


# ─────────────────────────────────────────────────────────────────────
# Blog
# ─────────────────────────────────────────────────────────────────────

def blog(request):
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('q', '')

    posts = BlogPost.objects.filter(status='published').select_related('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(excerpt__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(meta_keywords__icontains=search_query)
        )

    page_obj = Paginator(posts, 6).get_page(request.GET.get('page'))
    return render(request, 'blog.html', {
        'page_obj': page_obj,
        'categories': BlogCategory.objects.all(),
        'selected_category': get_object_or_404(BlogCategory, slug=category_slug) if category_slug else None,
        'search_query': search_query,
        # Paginator policzył już rekordy, drugie zapytanie zliczające było zbędne.
        'total_posts': page_obj.paginator.count,
    })


def blog_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)

    related = BlogPost.objects.filter(status='published', category=post.category).exclude(pk=post.pk)[:3]
    return render(request, 'blog_post_detail.html', {
        'post': post,
        'related_posts': related if post.category else [],
        'recent_posts': BlogPost.objects.filter(status='published').exclude(pk=post.pk)[:5],
    })


def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(category=category, status='published')
    return render(request, 'blog_category.html', {
        'category': category,
        'page_obj': Paginator(posts, 6).get_page(request.GET.get('page')),
    })


# ─────────────────────────────────────────────────────────────────────
# Punkty techniczne
# ─────────────────────────────────────────────────────────────────────

def healthcheck(request):
    """Zwraca tylko ok albo error, bez szczegółów o wnętrzu aplikacji."""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return HttpResponse('ok', content_type='text/plain')
    except Exception:
        logger.error('Health check nie powiódł się', exc_info=True)
        return HttpResponse('error', content_type='text/plain', status=500)


def get_client_ip(request):
    """Adres klienta na potrzeby rejestru zgód.

    X-Forwarded-For nie nadaje się na jedyne źródło: pierwszy wpis podaje sam
    klient, a serwery pośredniczące tylko dopisują się na koniec. Rejestr, który
    ma być dowodem wyrażenia zgody, nie może opierać się na wartości, którą
    odwiedzający wpisuje sobie dowolnie. Cloudflare dokłada własny nagłówek,
    którego klient nie nadpisze.
    """
    cloudflare = request.META.get('HTTP_CF_CONNECTING_IP')
    if cloudflare:
        return cloudflare.strip()
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@require_POST
def log_cookie_consent(request):
    """Zapisuje decyzję o cookies na potrzeby ścieżki audytowej RODO."""
    try:
        analytics = json.loads(request.body).get('analytics', False)
    except (ValueError, TypeError):
        logger.warning('Nieprawidłowe zgłoszenie zgody na cookies')
        # Treść wyjątku bywa fragmentem zapytania albo ścieżką na serwerze,
        # więc nie wraca do przeglądarki. Skrypt na stronie i tak jej nie używa.
        return JsonResponse({'status': 'error'}, status=400)

    CookieConsent.objects.create(
        analytics_consent=bool(analytics),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        session_key=request.session.session_key or '',
    )
    return JsonResponse({'status': 'success'})
