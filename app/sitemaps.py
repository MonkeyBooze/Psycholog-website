from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, BlogCategory


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'

    # Per-page priority: homepage highest, services high, info medium, legal low
    _priorities = {
        'home': 1.0,
        'diagnoza_adhd': 0.9,
        'diagnoza_autyzmu': 0.9,
        'trainings': 0.9,
        'pricing': 0.8,
        'about_us': 0.8,
        'contact': 0.8,
        'blog': 0.8,
        'privacy': 0.4,
        'cookie_policy': 0.4,
        'terms': 0.4,
        'data_subject_rights': 0.3,
    }

    def items(self):
        return list(self._priorities.keys())

    def priority(self, item):
        return self._priorities.get(item, 0.5)

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogCategory.objects.all()

    def location(self, item):
        return reverse('blog_category', kwargs={'slug': item.slug})
