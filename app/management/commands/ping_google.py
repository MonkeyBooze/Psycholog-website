from django.core.management.base import BaseCommand
from django.contrib.sitemaps import ping_google


class Command(BaseCommand):
    help = 'Ping Google to re-crawl the sitemap after deployment.'

    def handle(self, *args, **options):
        try:
            ping_google('/sitemap.xml')
            self.stdout.write(self.style.SUCCESS('Successfully pinged Google.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not ping Google: {e}'))
