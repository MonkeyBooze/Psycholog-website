from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .forms import AppointmentForm, DataSubjectRightsForm
from .models import Appointment, DataSubjectRightsRequest, BlogPost, BlogCategory, CookieConsent

def home(request):
    form = AppointmentForm()
    return render(request, 'home.html', {'form': form})

def book(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Save the appointment with GDPR consent data
            appointment = form.save(commit=False)
            appointment.data_processing_consent = form.cleaned_data.get('data_processing_consent', False)
            appointment.marketing_consent = form.cleaned_data.get('marketing_consent', False)
            if appointment.marketing_consent:
                appointment.marketing_consent_date = timezone.now()
            appointment.save()
            
            # Send email notifications
            try:
                if settings.EMAIL_HOST:
                    # Send confirmation email to customer
                    if appointment.email:
                        send_mail(
                            subject='Potwierdzenie umówienia wizyty - Gabinet Psychologiczny',
                            message=f"""
Szanowni Państwo {appointment.name},

Dziękujemy za umówienie wizyty w naszym gabinecie psychologicznym.

Szczegóły wizyty:
- Imię i nazwisko: {appointment.name}
- Telefon: {appointment.phone}
- Email: {appointment.email}
- Preferowany termin: {appointment.preferred_date or 'Nie podano'}
- Wiadomość: {appointment.message or 'Brak dodatkowych informacji'}

Skontaktujemy się z Państwem w ciągu 24 godzin w celu potwierdzenia dokładnego terminu wizyty.

W razie pytań prosimy o kontakt:
- Telefon: +48 606 841 722
- Email: {settings.EMAIL_FROM}

Z poważaniem,
Gabinet Psychologiczny
                            """,
                            from_email=settings.EMAIL_FROM,
                            recipient_list=[appointment.email],
                            fail_silently=True,
                        )
                    
                    # Send notification to admin(s)
                    admin_emails = getattr(settings, 'ADMIN_EMAILS', settings.EMAIL_FROM)
                    if isinstance(admin_emails, str):
                        admin_emails = [email.strip() for email in admin_emails.split(',')]

                    send_mail(
                        subject=f'Nowa wizyta - {appointment.name}',
                        message=f"""
NOWA WIZYTA UMÓWIONA:

Osoba: {appointment.name}
Telefon: {appointment.phone}
Email: {appointment.email or 'Nie podano'}
Preferowany termin: {appointment.preferred_date or 'Nie podano'}
Data zgłoszenia: {appointment.created_at.strftime('%d.%m.%Y %H:%M')}

Wiadomość od klienta:
{appointment.message or 'Brak dodatkowych informacji'}

ZGODY RODO:
- Przetwarzanie danych: {'TAK' if appointment.data_processing_consent else 'NIE'}
- Marketing: {'TAK' if appointment.marketing_consent else 'NIE'}

Skontaktuj się z klientem w ciągu 24h.
                        """,
                        from_email=settings.EMAIL_FROM,
                        recipient_list=admin_emails,
                        fail_silently=True,
                    )
                    
                    messages.success(request, 'Wizyta została umówiona pomyślnie! Otrzymali Państwo potwierdzenie na email.')
                else:
                    messages.success(request, 'Wizyta została umówiona pomyślnie!')
                    
            except Exception as e:
                messages.success(request, 'Wizyta została umówiona pomyślnie!')
            
            return redirect('thanks')
        return render(request, 'home.html', {'form': form})
    return redirect('home')

def thanks(request):
    return render(request, 'thanks.html')

def contact(request):
    form = AppointmentForm()
    return render(request, 'contact.html', {'form': form})

def privacy(request):
    return render(request, 'privacy.html')

def about_us(request):
    return render(request, 'about_us.html')

def pricing(request):
    return render(request, 'pricing.html')

def blog(request):
    # Get filters from request
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    
    # Base queryset - only published posts
    posts = BlogPost.objects.filter(status='published').select_related('category')
    
    # Apply filters
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(meta_keywords__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter sidebar
    categories = BlogCategory.objects.all()
    
    # Get selected category for display
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(BlogCategory, slug=category_slug)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'total_posts': posts.count(),
    }
    
    return render(request, 'blog.html', context)

def blog_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    
    # Get related posts (same category, excluding current post)
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(pk=post.pk)[:3] if post.category else []
    
    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(status='published').exclude(pk=post.pk)[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog_post_detail.html', context)

def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(category=category, status='published')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'blog_category.html', context)

def cookie_policy(request):
    return render(request, 'cookie_policy.html')

def terms(request):
    return render(request, 'terms.html')

def data_subject_rights(request):
    if request.method == 'POST':
        form = DataSubjectRightsForm(request.POST)
        if form.is_valid():
            # Check honeypot
            if form.cleaned_data.get('hp_field'):
                return redirect('data_subject_rights')
            
            # Save the request to database
            dsr_request = DataSubjectRightsRequest(
                request_type=form.cleaned_data['request_type'],
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                identification=form.cleaned_data['identification'],
                details=form.cleaned_data.get('details', ''),
                privacy_consent=form.cleaned_data['privacy_consent']
            )
            dsr_request.save()
            
            # Send confirmation email to user
            try:
                if settings.EMAIL_HOST:
                    send_mail(
                        subject=f'Potwierdzenie żądania RODO - {dsr_request.tracking_number}',
                        message=f"""
Szanowni Państwo,

Potwierdzamy otrzymanie Państwa żądania dotyczącego realizacji praw wynikających z RODO.

Numer referencyjny: {dsr_request.tracking_number}
Rodzaj żądania: {dsr_request.get_request_type_display()}
Data złożenia: {dsr_request.created_at.strftime('%d.%m.%Y %H:%M')}

Zgodnie z przepisami RODO, udzielimy odpowiedzi w terminie do 30 dni od daty otrzymania żądania.

W razie pytań prosimy o kontakt pod adresem email lub telefonicznie.

Z poważaniem,
{getattr(settings, 'SITE_NAME', 'Gabinet Psychologiczny')}
                        """,
                        from_email=settings.EMAIL_FROM,
                        recipient_list=[dsr_request.email],
                        fail_silently=True,
                    )
                    
                    # Send notification to admin(s)
                    admin_emails = getattr(settings, 'ADMIN_EMAILS', settings.EMAIL_FROM)
                    if isinstance(admin_emails, str):
                        admin_emails = [email.strip() for email in admin_emails.split(',')]

                    send_mail(
                        subject=f'Nowe żądanie RODO - {dsr_request.tracking_number}',
                        message=f"""
Otrzymano nowe żądanie RODO:

Numer: {dsr_request.tracking_number}
Rodzaj: {dsr_request.get_request_type_display()}
Osoba: {dsr_request.full_name}
Email: {dsr_request.email}
Telefon: {dsr_request.phone or 'Nie podano'}

Szczegóły w panelu administracyjnym.
                        """,
                        from_email=settings.EMAIL_FROM,
                        recipient_list=admin_emails,
                        fail_silently=True,
                    )
            except Exception:
                pass
            
            messages.success(
                request, 
                f'Twoje żądanie zostało złożone pomyślnie. Numer referencyjny: {dsr_request.tracking_number}'
            )
            return render(request, 'data_subject_rights.html', {
                'success': True, 
                'tracking_number': dsr_request.tracking_number
            })
        else:
            return render(request, 'data_subject_rights.html', {'form': form})
    else:
        form = DataSubjectRightsForm()
    
    return render(request, 'data_subject_rights.html', {'form': form})

def healthcheck(request):
    return HttpResponse("ok", content_type="text/plain", status=200)

@csrf_exempt
@require_POST
def log_cookie_consent(request):
    """Log user's cookie consent decision to database for audit trail"""
    try:
        data = json.loads(request.body)
        analytics_consent = data.get('analytics', False)

        # Get client information for audit
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        session_key = request.session.session_key or ''

        # Create consent log
        CookieConsent.objects.create(
            analytics_consent=analytics_consent,
            ip_address=ip_address,
            user_agent=user_agent,
            session_key=session_key
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_client_ip(request):
    """Helper function to get client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
