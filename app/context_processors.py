from django.conf import settings

def site_settings(request):
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'SITE_NAME': 'Spektrum Umysłu',
        'PRIMARY_COLOR': '#003366',
        'ACCENT_COLOR': '#006633',
    }
