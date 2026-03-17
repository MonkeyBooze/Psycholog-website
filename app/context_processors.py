from django.conf import settings

def site_settings(request):
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'GOOGLE_SITE_VERIFICATION': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
        'SITE_NAME': 'Spektrum Umysłu',
        'PRIMARY_COLOR': '#003366',
        'ACCENT_COLOR': '#006633',
    }
