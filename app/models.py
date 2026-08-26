from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

class Appointment(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30)
    preferred_date = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # GDPR consent fields
    data_processing_consent = models.BooleanField(default=False)
    data_processing_consent_date = models.DateTimeField(auto_now_add=True)
    marketing_consent = models.BooleanField(default=False)
    marketing_consent_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"


class TrainingInquiry(models.Model):
    """Zapytania ze zlikwidowanej strony szkoleń dla firm.

    Strona, widok i formularz zostały usunięte. Model i panel administracyjny
    zostają wyłącznie po to, żeby dało się odczytać zapytania zapisane wcześniej.
    ponytail: martwy model, do skasowania razem z tabelą, gdy potwierdzisz,
    że w panelu nie ma nic wartego zachowania.
    """
    SUBJECT_CHOICES = [
        ("antymobbingowe_pracownicy", "Szkolenie antymobbingowe dla pracowników"),
        ("antymobbingowe_kadra", "Szkolenie dla kadry zarządzającej i HR"),
        ("procedura", "Wdrożenie procedury antymobbingowej"),
        ("pakiet", "Pakiet PEŁNY"),
        ("inne", "Inne / Konsultacja"),
    ]

    name = models.CharField(max_length=120)
    company = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default="inne")
    message = models.TextField(blank=True)
    data_processing_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.name} ({self.created_at:%d.%m.%Y})"

    class Meta:
        verbose_name = "Training Inquiry"
        verbose_name_plural = "Training Inquiries"
        ordering = ["-created_at"]


class DataSubjectRightsRequest(models.Model):
    REQUEST_TYPES = [
        ('access', 'Żądanie dostępu do danych'),
        ('rectification', 'Żądanie sprostowania danych'),
        ('erasure', 'Żądanie usunięcia danych'),
        ('portability', 'Żądanie przenoszenia danych'),
        ('restriction', 'Żądanie ograniczenia przetwarzania'),
        ('objection', 'Sprzeciw wobec przetwarzania'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Oczekuje'),
        ('in_progress', 'W trakcie realizacji'),
        ('completed', 'Zakończone'),
        ('rejected', 'Odrzucone'),
    ]
    
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    identification = models.TextField()
    details = models.TextField(blank=True, null=True)
    privacy_consent = models.BooleanField(default=False)
    privacy_consent_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=20, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            import uuid
            self.tracking_number = f"DSR{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_request_type_display()} - {self.full_name} ({self.tracking_number})"
    
    class Meta:
        verbose_name = "Data Subject Rights Request"
        verbose_name_plural = "Data Subject Rights Requests"
        ordering = ['-created_at']


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Szkic'),
        ('published', 'Opublikowane'),
    ]

    title = models.CharField(max_length=200, help_text='Tytuł artykułu (ważny dla SEO)')
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text='URL artykułu (automatycznie generowany)')
    
    # SEO fields
    meta_description = models.CharField(
        max_length=160, 
        help_text='Opis dla wyszukiwarek (max 160 znaków)',
        blank=True
    )
    meta_keywords = models.CharField(
        max_length=255, 
        help_text='Słowa kluczowe oddzielone przecinkami',
        blank=True
    )
    
    # Content
    excerpt = models.TextField(max_length=300, help_text='Krótki opis artykułu (wyświetlany na liście)')
    content = models.TextField(help_text='Treść artykułu (obsługuje HTML)')
    featured_image = models.CharField(
        max_length=500, 
        blank=True, 
        help_text='URL do głównego zdjęcia artykułu'
    )
    
    # Relationships
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Publishing
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO fields
    read_time = models.PositiveIntegerField(default=5, help_text='Szacowany czas czytania w minutach')
    views_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Generate meta description if not provided
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_at', '-created_at']


class CookieConsent(models.Model):
    """Model to log user cookie consent decisions for GDPR compliance"""

    # Consent choice
    analytics_consent = models.BooleanField(
        default=False,
        help_text='Whether user consented to analytics cookies'
    )

    # Audit fields
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the user (for audit purposes)'
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text='Session identifier to track consent changes'
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text='Browser user agent string'
    )

    # Timestamps
    consented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        consent_type = "Accepted analytics" if self.analytics_consent else "Declined analytics"
        return f"{consent_type} - {self.consented_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Cookie Consent"
        verbose_name_plural = "Cookie Consents"
        ordering = ['-consented_at']
