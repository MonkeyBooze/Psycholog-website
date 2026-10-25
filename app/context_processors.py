import logging

from django.conf import settings
from django.db import DatabaseError
from django.utils.functional import SimpleLazyObject

from . import site_data
from .models import BlogPost


logger = logging.getLogger(__name__)


def _blog_has_posts():
    # A menu link must not take the page down with the database.
    try:
        return BlogPost.objects.filter(status='published').exists()
    except DatabaseError:
        logger.error('Blog menu link hidden: database unavailable', exc_info=True)
        return False


def _breadcrumb(path):
    """Ostatni element ścieżki okruszków dla danego adresu (pierwszym zawsze jest strona główna)."""
    names = {svc['path']: svc['name'] for svc in site_data.SERVICES.values()}
    names.update({loc['path']: f"Psycholog {loc['city']}" for loc in site_data.LOCATIONS})
    names.update({
        '/cennik/': 'Cennik',
        '/o-nas/': 'Zespół',
        '/kontakt/': 'Kontakt',
        '/blog/': 'Blog',
        '/standardy-ochrony-maloletnich/': 'Standardy Ochrony Małoletnich',
    })
    name = names.get(path)
    return [{'name': name, 'path': path}] if name else []


def site_settings(request):
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'GOOGLE_SITE_VERIFICATION': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
        'SITE_NAME': site_data.SITE_NAME,
        'SITE_URL': site_data.SITE_URL,
        'PRIMARY_COLOR': '#003366',
        'ACCENT_COLOR': '#006633',
        # Kontakt i lokalizacje — jedno źródło dla schematu, stopki i strony kontaktu.
        'PHONE_DISPLAY': site_data.PHONE_DISPLAY,
        'PHONE_SHORT': site_data.PHONE_SHORT,
        'PHONE_E164': site_data.PHONE_E164,
        'EMAIL': site_data.EMAIL,
        'ZNANYLEKARZ_URL': site_data.ZNANYLEKARZ_URL,
        'REVIEWS': site_data.REVIEWS,
        'LOCATIONS': site_data.LOCATIONS,
        'TEAM': site_data.TEAM,
        'BLOG_HAS_POSTS': SimpleLazyObject(_blog_has_posts),
        'BREADCRUMB': _breadcrumb(request.path),
        # Standardy Ochrony Małoletnich (obowiązek publikacji od 15.08.2024).
        'CHILD_PROTECTION': site_data.CHILD_PROTECTION,
        'CHILD_PROTECTION_SHORT': site_data.CHILD_PROTECTION_SHORT,
        'CHILD_PROTECTION_META': site_data.CHILD_PROTECTION_META,
        'OPENING_HOURS': site_data.OPENING_HOURS,
        # Ceny — patrz app/site_data.py, nie wpisywać ich ponownie w szablonach.
        'SERVICES': site_data.SERVICES,
        'LOGOPEDIA_PRICES': site_data.LOGOPEDIA_PRICES,
        'LOGOPEDIA_SCOPE': site_data.LOGOPEDIA_SCOPE,
        'LOGOPEDIA_STEPS': site_data.LOGOPEDIA_STEPS,
        'TUS_CYCLE_LENGTH': site_data.TUS_CYCLE_LENGTH,
        'TUS_CYCLE_PRICE': site_data.TUS_CYCLE_PRICE,
    }
