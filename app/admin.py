from django.contrib import admin
from .models import Appointment, DataSubjectRightsRequest, BlogCategory, BlogPost, StaffMember, CookieConsent


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at', 'data_processing_consent', 'marketing_consent']
    list_filter = ['created_at', 'data_processing_consent', 'marketing_consent']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'data_processing_consent_date', 'marketing_consent_date']


@admin.register(DataSubjectRightsRequest)
class DataSubjectRightsRequestAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'request_type', 'full_name', 'email', 'status', 'created_at']
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = ['tracking_number', 'full_name', 'email']
    readonly_fields = ['tracking_number', 'created_at', 'updated_at', 'privacy_consent_date']
    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('tracking_number', 'request_type', 'status')
        }),
        ('Dane osobowe', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Szczegóły żądania', {
            'fields': ('identification', 'details')
        }),
        ('Zgody i daty', {
            'fields': ('privacy_consent', 'privacy_consent_date', 'created_at', 'updated_at')
        })
    )


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'published_at', 'views_count', 'created_at']
    list_filter = ['status', 'category', 'published_at', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('title', 'slug', 'category', 'status')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Zawartość', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Ustawienia', {
            'fields': ('read_time', 'published_at')
        }),
        ('Statystyki', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')
    
    actions = ['make_published', 'make_draft']
    
    def make_published(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, f'{queryset.count()} artykułów zostało opublikowanych.')
    make_published.short_description = 'Opublikuj wybrane artykuły'
    
    def make_draft(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, f'{queryset.count()} artykułów zostało oznaczonych jako szkic.')
    make_draft.short_description = 'Oznacz jako szkic'


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'title', 'specialization', 'experience_years', 'is_active', 'display_order']
    list_filter = ['is_active', 'title']
    search_fields = ['first_name', 'last_name', 'title', 'specialization']
    list_editable = ['display_order', 'is_active']
    
    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('first_name', 'last_name', 'title', 'specialization')
        }),
        ('Doświadczenie zawodowe', {
            'fields': ('bio', 'education', 'experience_years')
        }),
        ('Kontakt', {
            'fields': ('email', 'phone')
        }),
        ('Media', {
            'fields': ('photo',)
        }),
        ('Ustawienia wyświetlania', {
            'fields': ('is_active', 'display_order')
        })
    )


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ['consented_at', 'analytics_consent', 'ip_address', 'session_key']
    list_filter = ['analytics_consent', 'consented_at']
    search_fields = ['ip_address', 'session_key']
    readonly_fields = ['consented_at', 'analytics_consent', 'ip_address', 'session_key', 'user_agent']
    date_hierarchy = 'consented_at'

    fieldsets = (
        ('Wybór użytkownika', {
            'fields': ('analytics_consent', 'consented_at')
        }),
        ('Informacje audytowe', {
            'fields': ('ip_address', 'session_key', 'user_agent')
        })
    )

    def has_add_permission(self, request):
        # Prevent manual creation - only logged via API
        return False

    def has_change_permission(self, request, obj=None):
        # Read-only for audit purposes
        return False
