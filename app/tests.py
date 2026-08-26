"""Testy pilnujące ustaleń z audytu SEO.

Każdy z nich odpowiada konkretnemu błędowi, który już raz wystąpił na produkcji.
Uruchomienie lokalnie (bez dotykania produkcyjnej bazy):

    DATABASE_URL=sqlite:///test.sqlite3 python manage.py test app

Bez tej zmiennej Django zbuduje bazę testowa obok bazy wskazanej w .env.
"""

import json
import re
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from app import site_data

# Strony statyczne (bez tych, które wymagają rekordów w bazie).
PAGES = [
    'home', 'about_us', 'pricing', 'contact', 'blog',
    'diagnoza_adhd', 'diagnoza_autyzmu', 'terapia_indywidualna',
    'konsultacje', 'tus', 'wsparcie_online', 'logopedia',
    'lokalizacja_opole', 'lokalizacja_nysa',
    'privacy', 'cookie_policy', 'terms', 'data_subject_rights', 'thanks',
    'standardy_ochrony_maloletnich',
]

# Strony usług — na nich wymagamy FAQ i danych FAQPage.
SERVICE_PAGES = [
    'diagnoza_adhd', 'diagnoza_autyzmu', 'terapia_indywidualna',
    'konsultacje', 'tus', 'wsparcie_online', 'logopedia',
]

# Strony, na których Google pokazuje tytuł i opis — limity długości.
MAX_TITLE = 60
MAX_DESCRIPTION = 160

INVISIBLE = ['​', '‌', '﻿', '⁠']

HOST = 'spektrumumyslu.pl'

# Produkcja serwuje pliki statyczne przez manifest WhiteNoise, który powstaje dopiero
# przy collectstatic. W testach go nie ma, więc podmieniamy backend na zwykły.
without_manifest = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


def get(client, name):
    return client.get(reverse(name), HTTP_HOST=HOST, secure=True)


def html_of(client, name):
    r = get(client, name)
    assert r.status_code == 200, f'{name} -> {r.status_code}'
    return r.content.decode('utf-8')


def strip_tags(html):
    html = re.sub(r'(?s)<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', html)
    return re.sub(r'\s+', ' ', re.sub(r'(?s)<[^>]+>', ' ', html))


def json_ld_blocks(html):
    return [json.loads(m) for m in
            re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', html)]


@without_manifest
class PagesRenderTests(TestCase):
    """Każda strona ma się wyrenderować. Regresja po zmianach w base.html jest cicha."""

    def test_all_pages_return_200(self):
        for name in PAGES:
            with self.subTest(page=name):
                self.assertEqual(get(self.client, name).status_code, 200)

    def test_sitemap_and_robots(self):
        for path in ('/sitemap.xml', '/robots.txt'):
            with self.subTest(path=path):
                self.assertEqual(
                    self.client.get(path, HTTP_HOST=HOST, secure=True).status_code, 200)

    def test_unknown_url_returns_404(self):
        self.assertEqual(
            self.client.get('/nie-ma-takiej-strony/', HTTP_HOST=HOST, secure=True).status_code,
            404)


@without_manifest
class SitemapTests(TestCase):
    """Sitemap wskazywał na example.com, bo django.contrib.sites nie miał domeny."""

    def test_sitemap_uses_real_domain_not_example_com(self):
        body = self.client.get('/sitemap.xml', HTTP_HOST=HOST, secure=True).content.decode()
        self.assertNotIn('example.com', body)
        self.assertIn(f'<loc>{site_data.SITE_URL}/</loc>', body)

    def test_sitemap_covers_every_public_page(self):
        body = self.client.get('/sitemap.xml', HTTP_HOST=HOST, secure=True).content.decode()
        for name in PAGES:
            if name == 'thanks':      # celowo poza indeksem
                continue
            with self.subTest(page=name):
                self.assertIn(f'<loc>{site_data.SITE_URL}{reverse(name)}</loc>', body)

    def test_location_pages_are_in_sitemap(self):
        body = self.client.get('/sitemap.xml', HTTP_HOST=HOST, secure=True).content.decode()
        for loc in site_data.LOCATIONS:
            with self.subTest(city=loc['city']):
                self.assertIn(f'<loc>{site_data.SITE_URL}{loc["path"]}</loc>', body)


@without_manifest
class MetaTagTests(TestCase):
    """Tytuły ucinane w wynikach, opisy powyżej 160 znaków, brakujący kanoniczny."""

    def test_title_within_serp_limit(self):
        for name in PAGES:
            html = html_of(self.client, name)
            title = re.search(r'<title>(.*?)</title>', html, re.S).group(1)
            title = re.sub(r'\s+', ' ', title).strip()
            with self.subTest(page=name, title=title):
                self.assertTrue(title, f'{name}: pusty tytuł')
                self.assertLessEqual(len(title), MAX_TITLE, f'{name}: {len(title)} znaków')

    def test_description_within_serp_limit(self):
        for name in PAGES:
            html = html_of(self.client, name)
            desc = re.search(r'<meta name="description" content="(.*?)">', html, re.S).group(1)
            desc = re.sub(r'\s+', ' ', desc).strip()
            with self.subTest(page=name, desc=desc):
                self.assertTrue(desc, f'{name}: pusty opis')
                self.assertLessEqual(len(desc), MAX_DESCRIPTION, f'{name}: {len(desc)} znaków')

    def test_description_has_no_newlines(self):
        """Opisy łamane w szablonie wstawiały znak nowej linii do atrybutu."""
        for name in PAGES:
            html = html_of(self.client, name)
            raw = re.search(r'<meta name="description" content="(.*?)">', html, re.S).group(1)
            with self.subTest(page=name):
                self.assertNotIn('\n', raw)

    def test_canonical_is_absolute_and_on_site_domain(self):
        for name in PAGES:
            html = html_of(self.client, name)
            canonical = re.search(r'<link rel="canonical" href="(.*?)">', html).group(1)
            with self.subTest(page=name, canonical=canonical):
                self.assertTrue(canonical.startswith(site_data.SITE_URL + '/'))

    def test_exactly_one_h1_per_page(self):
        for name in PAGES:
            html = html_of(self.client, name)
            with self.subTest(page=name):
                self.assertEqual(len(re.findall(r'<h1[\s>]', html)), 1)

    def test_og_image_is_absolute_url(self):
        """og:image podawany względnie nie działa — Open Graph wymaga pełnego adresu."""
        for name in PAGES:
            html = html_of(self.client, name)
            og = re.search(r'<meta property="og:image" content="(.*?)">', html).group(1)
            with self.subTest(page=name, og=og):
                self.assertTrue(og.startswith('https://'))

    def test_no_invisible_characters_in_output(self):
        """W atrybutach alt siedziały znaki U+200B rozbijające słowa kluczowe."""
        for name in PAGES:
            html = html_of(self.client, name)
            for ch in INVISIBLE:
                with self.subTest(page=name, char=hex(ord(ch))):
                    self.assertNotIn(ch, html)


@without_manifest
class StructuredDataTests(TestCase):
    """Schema miała zduplikowane obiekty, błędną specjalizację i cudze oceny."""

    def test_json_ld_is_valid_json_on_every_page(self):
        for name in PAGES:
            html = html_of(self.client, name)
            with self.subTest(page=name):
                blocks = json_ld_blocks(html)   # rzuci ValueError przy błędnym JSON
                self.assertTrue(blocks, f'{name}: brak danych strukturalnych')

    def test_no_aggregate_rating_anywhere(self):
        """Oceny pochodzą z ZnanyLekarz — oznaczanie ich jako własnych łamie wytyczne."""
        for name in PAGES:
            blocks = json_ld_blocks(html_of(self.client, name))
            with self.subTest(page=name):
                self.assertNotIn('aggregateRating', json.dumps(blocks))

    def test_one_business_node_per_location_with_unique_id(self):
        graph = json_ld_blocks(html_of(self.client, 'home'))[0]['@graph']
        ids = [n['@id'] for n in graph if 'Psychologist' in n.get('@type', [])]
        self.assertEqual(len(ids), len(site_data.LOCATIONS))
        self.assertEqual(len(set(ids)), len(ids), 'gabinety mają ten sam @id')
        for loc in site_data.LOCATIONS:
            self.assertIn(f'{site_data.SITE_URL}{loc["path"]}#gabinet', ids)

    def test_business_nodes_are_not_marked_as_psychiatry(self):
        html = html_of(self.client, 'home')
        self.assertNotIn('"Psychiatry"', html)

    def test_opening_hours_declared_once_and_match_site_data(self):
        graph = json_ld_blocks(html_of(self.client, 'home'))[0]['@graph']
        for node in graph:
            if 'Psychologist' not in node.get('@type', []):
                continue
            spec = node['openingHoursSpecification'][0]
            self.assertEqual(spec['opens'], site_data.OPENING_HOURS['opens'])
            self.assertEqual(spec['closes'], site_data.OPENING_HOURS['closes'])

    def test_service_pages_expose_faqpage(self):
        for name in SERVICE_PAGES:
            html = html_of(self.client, name)
            with self.subTest(page=name):
                types = [b.get('@type') for b in json_ld_blocks(html)]
                self.assertIn('FAQPage', types, f'{name}: brak FAQPage')

    def test_faq_schema_answers_are_visible_on_the_page(self):
        """Google wymaga, żeby treść FAQPage była widoczna na stronie."""
        for name in SERVICE_PAGES:
            html = html_of(self.client, name)
            text = strip_tags(html)
            faq = next(b for b in json_ld_blocks(html) if b.get('@type') == 'FAQPage')
            for item in faq['mainEntity']:
                question = re.sub(r'\s+', ' ', item['name']).strip()
                with self.subTest(page=name, question=question[:50]):
                    self.assertIn(question, text)


@without_manifest
class PriceConsistencyTests(TestCase):
    """Diagnoza ADHD kosztowała 400 zł na jednej podstronie i 500 zł na drugiej."""

    STALE = ['400 zł', '600 zł', '100 zł', '1000 zł na', '150 - 180']

    def test_no_stale_prices_in_service_pages(self):
        for name in SERVICE_PAGES + ['home', 'pricing']:
            html = html_of(self.client, name)
            for stale in self.STALE:
                with self.subTest(page=name, price=stale):
                    self.assertNotIn(stale, html)

    def test_each_service_page_shows_its_price_from_site_data(self):
        pairs = [
            ('diagnoza_adhd', 'adhd'),
            ('diagnoza_autyzmu', 'autyzm'),
            ('tus', 'tus'),
            ('terapia_indywidualna', 'terapia'),
            ('konsultacje', 'konsultacja'),
            ('wsparcie_online', 'online'),
            ('logopedia', 'logopedia'),
        ]
        for page, key in pairs:
            html = html_of(self.client, page)
            with self.subTest(page=page):
                self.assertIn(f'{site_data.SERVICES[key]["price"]} zł', html)

    def test_no_price_on_any_page_is_unknown_to_site_data(self):
        """Każda kwota widoczna na stronie musi pochodzić z app/site_data.py.

        Cena diagnozy ADHD siedziała w treści odpowiedzi FAQ i w opisie meta,
        więc po podniesieniu stawki w cenniku strona usługi dalej podawała starą.
        """
        znane = {str(v['price']) for v in site_data.SERVICES.values()}
        znane |= {str(b['price']) for v in site_data.SERVICES.values()
                  for b in v.get('price_breakdown', [])}
        znane |= {str(item['price']) for item in site_data.LOGOPEDIA_PRICES}
        znane.add(str(site_data.TUS_CYCLE_PRICE))

        obce = []
        for name in PAGES:
            html = self.client.get(reverse(name)).content.decode()
            for kwota in re.findall(r'(\d{2,5})\s*(?:zł|PLN)', html):
                if kwota not in znane:
                    obce.append(f'{name}: {kwota}')
        self.assertEqual(sorted(set(obce)), [],
                         'kwota, której nie ma w site_data, czyli rozjazd cen')

    def test_no_provisional_prices_left(self):
        """Cena oznaczona jako prowizoryczna nie może trafić na produkcję.

        Usuń klucz `provisional_price` w app/site_data.py dopiero po potwierdzeniu stawki.
        """
        provisional = [key for key, svc in site_data.SERVICES.items()
                       if svc.get('provisional_price')]
        self.assertEqual(
            provisional, [],
            f'ceny do potwierdzenia przez właściciela: {provisional}')

    def test_pricing_page_lists_every_service(self):
        html = html_of(self.client, 'pricing')
        for key, svc in site_data.SERVICES.items():
            with self.subTest(service=key):
                self.assertIn(f'{svc["price"]}', html)


@without_manifest
class NapConsistencyTests(TestCase):
    """W serwisie były trzy różne zestawy godzin i adres bez numeru."""

    def test_every_page_uses_one_phone_number(self):
        for name in PAGES:
            html = html_of(self.client, name)
            numbers = set(re.findall(r'tel:(\+?\d+)', html))
            with self.subTest(page=name):
                self.assertLessEqual(numbers, {site_data.PHONE_E164})

    def test_opening_hours_appear_only_in_one_form(self):
        for name in ['contact', 'home', 'lokalizacja_opole', 'lokalizacja_nysa']:
            text = strip_tags(html_of(self.client, name))
            for stale in ['8:00-18:00', '8:00 - 18:00', '08:00-22:00', '8:00 - 22:00']:
                with self.subTest(page=name, hours=stale):
                    self.assertNotIn(stale, text)

    def test_full_street_address_on_contact_and_location_pages(self):
        for name in ['contact', 'lokalizacja_opole', 'lokalizacja_nysa']:
            html = html_of(self.client, name)
            with self.subTest(page=name):
                self.assertTrue(
                    any(loc['street'] in html for loc in site_data.LOCATIONS),
                    f'{name}: brak pełnego adresu z numerem')


@without_manifest
class InternalLinkTests(TestCase):
    """Cennik i strona zespołu były osierocone — zero linków z treści."""

    def _body_links(self, name):
        html = html_of(self.client, name)
        main = re.search(r'(?s)<main.*?</main>', html)
        return set(re.findall(r'href="(/[^"#]*)"', main.group(0) if main else ''))

    def test_service_pages_link_to_pricing(self):
        for name in SERVICE_PAGES:
            with self.subTest(page=name):
                self.assertIn('/cennik/', self._body_links(name))

    def test_service_pages_link_to_a_location_page(self):
        paths = {loc['path'] for loc in site_data.LOCATIONS}
        for name in SERVICE_PAGES:
            with self.subTest(page=name):
                self.assertTrue(self._body_links(name) & paths)

    def test_pricing_table_links_to_every_service(self):
        """Każdy wiersz tabeli cennika prowadzi na stronę swojej usługi.

        Logopedia nie ma tam wiersza zbiorczego, tylko trzy własne pozycje.
        Bez odnośnika w nich tabela byłaby jedynym miejscem, gdzie usługa jest
        wymieniona, a nie da się z niej przejść dalej. Sprawdzamy samą tabelę,
        bo niżej na stronie są jeszcze karty usług i one zawsze linkują.
        """
        html = html_of(self.client, 'pricing')
        tabela = re.search(r'(?s)<tbody>.*?</tbody>', html)
        self.assertIsNotNone(tabela, 'brak tabeli cennika')
        links = set(re.findall(r'href="(/[^"#]*)"', tabela.group(0)))
        for key, svc in site_data.SERVICES.items():
            with self.subTest(service=key):
                self.assertIn(svc['path'], links)

    def test_location_pages_link_to_services_available_there(self):
        """Strona gabinetu wymienia usługi prowadzone w tym mieście i tylko je.

        TUS jest prowadzony wyłącznie w Opolu, więc strona Nysy nie może go
        oferować, a strona Opola nie może go pominąć.
        """
        for loc in site_data.LOCATIONS:
            links = self._body_links(f'lokalizacja_{loc["slug"]}')
            niedostepne = loc.get('unavailable_services', [])
            for key, svc in site_data.SERVICES.items():
                with self.subTest(city=loc['city'], service=key):
                    if key in niedostepne:
                        self.assertNotIn(svc['path'], links)
                    else:
                        self.assertIn(svc['path'], links)


class StaticAssetTests(SimpleTestCase):
    """Szablon wskazywał na obrazek, którego nie było w repozytorium."""

    def test_every_referenced_image_exists_on_disk(self):
        root = Path(settings.BASE_DIR) / 'app' / 'static'
        missing = []
        for tpl in (Path(settings.BASE_DIR) / 'app' / 'templates').rglob('*.html'):
            for ref in re.findall(r"{%\s*static\s*'([^']+)'\s*%}", tpl.read_text(encoding='utf-8')):
                if not (root / ref).exists():
                    missing.append(f'{tpl.name}: {ref}')
        # url() w CSS też trafia do manifestu — zły odnośnik wysypuje collectstatic.
        for css in (root / 'css').rglob('*.css'):
            for ref in re.findall(r"url\(['\"]?/static/([^'\")]+)", css.read_text(encoding='utf-8')):
                if not (root / ref).exists():
                    missing.append(f'{css.name}: {ref}')
        self.assertEqual(missing, [])

    def test_static_filenames_are_lowercase_ascii(self):
        """Wielkie litery i polskie znaki w nazwach plików psują się na Linuksie."""
        root = Path(settings.BASE_DIR) / 'app' / 'static'
        assets = {'.jpg', '.jpeg', '.png', '.svg', '.webp', '.gif', '.ico',
                  '.css', '.js', '.woff', '.woff2'}
        bad = [str(p.relative_to(root)) for p in root.rglob('*')
               if p.is_file() and p.suffix.lower() in assets
               and (p.name != p.name.lower() or not p.name.isascii())]
        self.assertEqual(bad, [])

    def test_no_image_over_300kb(self):
        root = Path(settings.BASE_DIR) / 'app' / 'static' / 'images'
        heavy = [f'{p.name}: {p.stat().st_size // 1024} kB'
                 for p in root.glob('*') if p.is_file() and p.stat().st_size > 300 * 1024]
        self.assertEqual(heavy, [])

    def test_css_does_not_import_remote_fonts(self):
        """@import fontów z CSS tworzy dodatkową rundę pobierania przed renderem."""
        css = (Path(settings.BASE_DIR) / 'app' / 'static' / 'css' / 'main.css').read_text(encoding='utf-8')
        self.assertNotIn('fonts.googleapis.com', css)


class RenderVisibilityTests(SimpleTestCase):
    """Treść musi być widoczna bez JavaScriptu i bez przewijania strony.

    Sekcje miały opacity: 0 i dostawały klasę .visible dopiero od
    IntersectionObservera. Renderer Google nie przewija strony, więc wszystko
    poniżej pierwszego ekranu zostawało niewidoczne, a nagłówek H1 pojawiał się
    dopiero po 800 ms animacji, co opóźniało Largest Contentful Paint.
    """

    CSS_ROOT = Path(settings.BASE_DIR) / 'app' / 'static' / 'css'

    def test_no_css_rule_hides_content_by_default(self):
        pattern = re.compile(r'([^{}]+)\{[^{}]*opacity:\s*0\s*[;}]')
        hidden = []
        for css in self.CSS_ROOT.rglob('*.css'):
            for selector in pattern.findall(css.read_text(encoding='utf-8')):
                selector = ' '.join(selector.split())
                # Natywny checkbox chowany pod własnym znacznikiem .checkmark.
                if 'checkbox' in selector:
                    continue
                hidden.append(f'{css.name}: {selector}')
        self.assertEqual(hidden, [], 'CSS ukrywa treść, zanim uruchomi się JavaScript')

    def test_reveal_does_not_depend_on_scrolling(self):
        base = (Path(settings.BASE_DIR) / 'app' / 'templates' / 'base.html').read_text(encoding='utf-8')
        self.assertFalse('IntersectionObserver' in base,
                         'pojawienie się treści zależy od przewinięcia strony')


class DomainTests(SimpleTestCase):
    """Stara domena nie należy już do właściciela i nie może zostawać w konfiguracji."""

    OLD = 'psychoedukacjaopole.pl'

    def test_old_domain_absent_from_settings_and_code(self):
        for rel in ['project/settings.py', 'project/middleware.py', 'app/site_data.py']:
            with self.subTest(file=rel):
                self.assertNotIn(
                    self.OLD, (Path(settings.BASE_DIR) / rel).read_text(encoding='utf-8'))

    def test_old_domain_not_in_allowed_hosts(self):
        self.assertNotIn(self.OLD, ' '.join(settings.ALLOWED_HOSTS))


@without_manifest
class ChildProtectionTests(TestCase):
    """Publikacja Standardów Ochrony Małoletnich na stronie jest obowiązkiem ustawowym.

    Art. 22c ustawy z 13 maja 2016 r. wymaga udostępnienia dokumentu w dwóch wersjach:
    pełnej oraz skróconej, zrozumiałej dla małoletnich.
    """

    def test_page_is_reachable_and_linked_from_footer(self):
        url = reverse('standardy_ochrony_maloletnich')
        self.assertEqual(get(self.client, 'standardy_ochrony_maloletnich').status_code, 200)
        for name in ('home', 'contact', 'pricing'):
            with self.subTest(page=name):
                self.assertIn(f'href="{url}"', html_of(self.client, name))

    def test_both_required_versions_are_published(self):
        html = html_of(self.client, 'standardy_ochrony_maloletnich')
        text = strip_tags(html)
        for title, _ in site_data.CHILD_PROTECTION:
            with self.subTest(section=title[:40]):
                self.assertIn(title, text)
        for title, _ in site_data.CHILD_PROTECTION_SHORT:
            with self.subTest(short=title[:40]):
                self.assertIn(title, text)

    def test_statutory_topics_are_covered(self):
        """Art. 22b wymienia zagadnienia, które dokument musi regulować."""
        text = strip_tags(html_of(self.client, 'standardy_ochrony_maloletnich')).lower()
        for topic in ['bezpiecznych relacji', 'zachowania niedozwolone', 'interwencji',
                      'sąd', 'niebieskiej karty', 'rejestrze sprawców', 'wizerunk',
                      'plan wsparcia', 'przegląd']:
            with self.subTest(topic=topic):
                self.assertIn(topic, text)

    def test_placeholders_are_filled_before_publication(self):
        """Dokument prawny nie może wyjść na produkcję z polami DO UZUPEŁNIENIA."""
        missing = [k for k, v in site_data.CHILD_PROTECTION_META.items()
                   if isinstance(v, str) and 'DO UZUPEŁNIENIA' in v]
        self.assertEqual(missing, [], f'pola do uzupełnienia przez właściciela: {missing}')


# Poczta w testach: własny backend zbierający wiadomości, plus dane logowania,
# których brak wyłącza wysyłkę. Bez tego wynik zależałby od lokalnego pliku .env.
with_email = override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_HOST_USER='test@example.com',
    EMAIL_HOST_PASSWORD='haslo-testowe',
    EMAIL_FROM='no-reply@example.com',
    ADMIN_NOTIFICATION_EMAIL='gabinet@example.com',
)


@without_manifest
@with_email
class BookingFlowTests(TestCase):
    """Zgłoszenia nie docierały mailem, więc ścieżka wysyłki ma własne testy.

    Wcześniej mail szedł z wątku daemon, którego Railway ubija przy wymianie
    procesu, a niepowodzenie lądowało w logu jako informacja.
    """

    PAYLOAD = {
        'name': 'Anna Kowalska',
        'phone': '600100200',
        'email': 'anna@example.com',
        'subject': 'logopedia',
        'data_processing_consent': 'on',
        'hp_field': '',
    }

    def test_booking_saves_and_sends_two_emails(self):
        from django.core import mail
        from app.models import Appointment

        response = self.client.post(reverse('book'), self.PAYLOAD)
        self.assertRedirects(response, reverse('thanks'))

        appointment = Appointment.objects.get()
        self.assertEqual(appointment.name, 'Anna Kowalska')
        # Zgoda zapisuje się przez ModelForm, wcześniej robił to ręcznie widok.
        self.assertTrue(appointment.data_processing_consent)

        odbiorcy = sorted(address for wiadomosc in mail.outbox for address in wiadomosc.to)
        self.assertEqual(odbiorcy, ['anna@example.com', 'gabinet@example.com'])

    def test_email_names_the_service_the_way_the_price_list_does(self):
        """Mail mówił „Diagnoza autyzmu (ADOS-2)”, a cennik „Diagnoza spektrum autyzmu”."""
        from django.core import mail

        self.client.post(reverse('book'), dict(self.PAYLOAD, subject='autyzm'))
        do_gabinetu = next(w for w in mail.outbox if 'gabinet@example.com' in w.to)
        self.assertIn(site_data.SERVICES['autyzm']['name'], do_gabinetu.body)

    def test_booking_without_consent_saves_nothing(self):
        from django.core import mail
        from app.models import Appointment

        payload = dict(self.PAYLOAD)
        del payload['data_processing_consent']
        self.client.post(reverse('book'), payload)

        self.assertEqual(Appointment.objects.count(), 0)
        self.assertEqual(mail.outbox, [])

    def test_honeypot_blocks_the_submission(self):
        from app.models import Appointment

        self.client.post(reverse('book'), dict(self.PAYLOAD, hp_field='bot'))
        self.assertEqual(Appointment.objects.count(), 0)


class EmailConfigurationTests(TestCase):
    """Brak danych logowania musi być głośny, bo to najczęstsza przyczyna braku maili."""

    @override_settings(EMAIL_HOST_USER='', EMAIL_HOST_PASSWORD='')
    def test_missing_credentials_are_logged_as_error(self):
        from app.models import Appointment

        with self.assertLogs('app.views', level='ERROR') as log:
            self.client.post(reverse('book'), BookingFlowTests.PAYLOAD)

        # Zgłoszenie nie może przepaść tylko dlatego, że poczta nie działa.
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertTrue(any('nieskonfigurowana' in wiersz.lower() for wiersz in log.output))


class ClientIpTests(SimpleTestCase):
    """Rejestr zgód ma być dowodem, więc nie może ufać nagłówkowi od klienta."""

    def _ip(self, **meta):
        from django.test import RequestFactory
        from app.views import get_client_ip
        return get_client_ip(RequestFactory().get('/', **meta))

    def test_cloudflare_header_wins(self):
        address = self._ip(HTTP_CF_CONNECTING_IP='203.0.113.7',
                         HTTP_X_FORWARDED_FOR='1.2.3.4, 203.0.113.7')
        self.assertEqual(address, '203.0.113.7')

    def test_spoofed_first_entry_is_ignored(self):
        """Pierwszy wpis X-Forwarded-For podaje sam klient, liczy się ostatni."""
        address = self._ip(HTTP_X_FORWARDED_FOR='6.6.6.6, 198.51.100.20')
        self.assertEqual(address, '198.51.100.20')


class PhoneConsistencyTests(SimpleTestCase):
    """Numer telefonu był wklejony w 22 miejscach mimo że site_data go udostępnia."""

    # Strona 500 renderuje się bez procesorów kontekstu, więc numer musi tam
    # zostać wpisany wprost. To jedyny dozwolony wyjątek.
    WYJATKI = {'500.html'}

    def test_phone_number_is_not_hardcoded_in_templates(self):
        directory = Path(settings.BASE_DIR) / 'app' / 'templates'
        hardcoded = [
            str(p.relative_to(directory))
            for p in directory.rglob('*.html')
            if p.name not in self.WYJATKI
            and re.search(r'606\s?841\s?722', p.read_text(encoding='utf-8'))
        ]
        self.assertEqual(hardcoded, [])

    def test_phone_number_is_not_hardcoded_in_python(self):
        directory = Path(settings.BASE_DIR) / 'app'
        hardcoded = [
            str(p.relative_to(directory))
            for p in directory.rglob('*.py')
            if p.name != 'site_data.py' and 'tests' not in p.name
            and re.search(r'606\s?841\s?722', p.read_text(encoding='utf-8'))
        ]
        self.assertEqual(hardcoded, [])


class StaticReferenceTests(SimpleTestCase):
    """Windows nie rozróżnia wielkości liter w nazwach plików, Linux rozróżnia.

    W repozytorium leżało images/Logo.png, a szablon prosił o images/logo.png.
    Lokalnie działało, bo system plików uznaje te nazwy za tę samą. Na serwerze
    collectstatic zbudował manifest z kluczem images/Logo.png, więc {% static %}
    nie znajdował wpisu i podnosił ValueError przy renderowaniu base.html,
    czyli na każdej podstronie serwisu.

    Punktem odniesienia jest git, bo to jego zapis nazw trafia na serwer.
    """

    def _repository_files(self):
        """Zawartość gita plus pliki jeszcze niezacommitowane, ale nieignorowane,
        czyli dokładnie to, co znajdzie się na serwerze po najbliższym wdrożeniu."""
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                cwd=settings.BASE_DIR,
                capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            self.skipTest('git niedostępny')
        if result.returncode:
            self.skipTest('directory nie jest repozytorium git')
        return {line for line in result.stdout.splitlines() if line}

    def test_static_references_match_repository_filenames(self):
        tracked = self._repository_files()
        directory = Path(settings.BASE_DIR) / 'app' / 'templates'
        missing = []
        for template in directory.rglob('*.html'):
            for reference in re.findall(r"""{%\s*static\s+['"]([^'"]+)['"]""",
                                    template.read_text(encoding='utf-8')):
                if f'app/static/{reference}' not in tracked:
                    missing.append(f'{template.name}: {reference}')
        self.assertEqual(
            missing, [],
            'szablon odwołuje się do pliku, którego nie ma w repozytorium '
            '(najczęściej rozjazd wielkości liter): ' + str(missing))

    def test_repository_filenames_match_the_filesystem(self):
        """Na Windowsie git potrafi trzymać starą wielkość liter po zmianie nazwy."""
        tracked = self._repository_files()
        mismatched = []
        for wpis in tracked:
            path = Path(settings.BASE_DIR) / wpis
            directory = path.parent
            if directory.is_dir() and path.name not in {x.name for x in directory.iterdir()}:
                mismatched.append(wpis)
        self.assertEqual(mismatched, [], f'git i dysk różnią się nazwami: {mismatched}')


class EmailConsistencyTests(SimpleTestCase):
    """Adres był wklejony w 17 miejscach, tak samo jak wcześniej numer telefonu."""

    def test_contact_email_is_not_hardcoded_in_templates(self):
        directory = Path(settings.BASE_DIR) / 'app' / 'templates'
        hardcoded = [
            str(p.relative_to(directory))
            for p in directory.rglob('*.html')
            if site_data.EMAIL in p.read_text(encoding='utf-8')
        ]
        self.assertEqual(hardcoded, [])
