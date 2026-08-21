"""Testy pilnujące ustaleń z audytu SEO.

Każdy z nich odpowiada konkretnemu błędowi, który już raz wystąpił na produkcji.
Uruchomienie lokalnie (bez dotykania produkcyjnej bazy):

    DATABASE_URL=sqlite:///test.sqlite3 python manage.py test app

Bez tej zmiennej Django zbuduje bazę testowa obok bazy wskazanej w .env.
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from app import site_data

# Strony statyczne (bez tych, które wymagają rekordów w bazie).
PAGES = [
    'home', 'about_us', 'pricing', 'contact', 'blog',
    'diagnoza_adhd', 'diagnoza_autyzmu', 'terapia_indywidualna',
    'konsultacje', 'tus', 'wsparcie_online', 'logopedia', 'trainings',
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

    def test_location_pages_link_to_every_service(self):
        for name in ['lokalizacja_opole', 'lokalizacja_nysa']:
            links = self._body_links(name)
            for key, svc in site_data.SERVICES.items():
                with self.subTest(page=name, service=key):
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
