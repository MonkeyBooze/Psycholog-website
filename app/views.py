from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, F

from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
import json
import threading
import logging
from .forms import AppointmentForm, DataSubjectRightsForm, TrainingInquiryForm
from .models import Appointment, DataSubjectRightsRequest, BlogPost, BlogCategory, CookieConsent, TrainingInquiry

logger = logging.getLogger(__name__)


def sendAdminNotification(subject, body):
    """Send an email notification directly to the admin."""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.EMAIL_FROM,
            recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
            fail_silently=False,
        )
        logger.info("Admin notification sent to %s", settings.ADMIN_NOTIFICATION_EMAIL)
    except Exception as exc:
        logger.error("Admin notification failed: %s", exc)


def home(request):
    form = AppointmentForm()
    return render(request, 'home.html', {'form': form})

SUBJECT_MAP = {
    "terapia": "Terapia indywidualna",
    "konsultacja": "Konsultacja psychologiczna",
    "adhd": "Diagnoza ADHD",
    "autyzm": "Diagnoza autyzmu (ADOS-2)",
    "tus": "Trening Umiejętności Społecznych",
    "inne": "Inne",
}


def _sendBookingEmails(name, phone, email, subject_label, created_at, data_processing_consent, marketing_consent):
    """Send booking emails in a background thread so the user isn't blocked."""
    try:
        email_configured = (
            settings.EMAIL_HOST and
            settings.EMAIL_HOST.strip() and
            settings.EMAIL_HOST_USER and
            settings.EMAIL_HOST_USER.strip()
        )
        if not email_configured:
            logger.info("Email not configured - skipping email notifications")
            return

        # Send confirmation email to customer
        if email:
            send_mail(
                subject="Potwierdzenie umówienia wizyty - Gabinet Psychologiczny",
                message=(
                    f"Szanowni Państwo {name},\n\n"
                    f"Dziękujemy za umówienie wizyty w naszym gabinecie psychologicznym.\n\n"
                    f"Szczegóły wizyty:\n"
                    f"- Imię i nazwisko: {name}\n"
                    f"- Telefon: {phone}\n"
                    f"- Email: {email}\n"
                    f"- Temat: {subject_label}\n\n"
                    f"Skontaktujemy się z Państwem w ciągu 24 godzin w celu potwierdzenia dokładnego terminu wizyty.\n\n"
                    f"W razie pytań prosimy o kontakt:\n"
                    f"- Telefon: +48 606 841 722\n"
                    f"- Email: {settings.EMAIL_FROM}\n\n"
                    f"Z poważaniem,\nGabinet Psychologiczny"
                ),
                from_email=settings.EMAIL_FROM,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info("Confirmation email sent to %s", email)

        # Send notification to admin
        sendAdminNotification(
            subject=f"Nowa wizyta - {name}",
            body=(
                f"NOWA WIZYTA UMÓWIONA:\n\n"
                f"Osoba: {name}\n"
                f"Telefon: {phone}\n"
                f"Email: {email or 'Nie podano'}\n"
                f"Temat: {subject_label}\n"
                f"Data zgłoszenia: {created_at}\n\n"
                f"ZGODY RODO:\n"
                f"- Przetwarzanie danych: {'TAK' if data_processing_consent else 'NIE'}\n"
                f"- Marketing: {'TAK' if marketing_consent else 'NIE'}\n\n"
                f"Skontaktuj się z klientem w ciągu 24h."
            ),
        )
        logger.info("Admin notification sent")
    except Exception as exc:
        logger.error("Background email sending failed: %s", exc)


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def book(request):
    if request.method == 'POST':
        logger.info("Booking form submitted")

        form = AppointmentForm(request.POST)

        if form.is_valid():
            logger.info("Form is valid")
            try:
                # Save the appointment with GDPR consent data
                appointment = form.save(commit=False)
                appointment.data_processing_consent = form.cleaned_data.get('data_processing_consent', False)
                appointment.marketing_consent = form.cleaned_data.get('marketing_consent', False)

                if appointment.marketing_consent:
                    appointment.marketing_consent_date = timezone.now()

                appointment.save()
                logger.info(f"Appointment saved successfully: ID {appointment.id}")

                # Capture subject from POST (not a model field)
                raw_subject = request.POST.get('subject', '')
                subject_label = SUBJECT_MAP.get(raw_subject, raw_subject or 'Nie podano')

                # Send emails in background thread (user gets instant response)
                thread = threading.Thread(
                    target=_sendBookingEmails,
                    kwargs={
                        "name": appointment.name,
                        "phone": appointment.phone,
                        "email": appointment.email or "",
                        "subject_label": subject_label,
                        "created_at": appointment.created_at.strftime("%d.%m.%Y %H:%M"),
                        "data_processing_consent": appointment.data_processing_consent,
                        "marketing_consent": appointment.marketing_consent,
                    },
                    daemon=True,
                )
                thread.start()

                messages.success(request, 'Wizyta została umówiona pomyślnie!')
                return redirect('thanks')

            except Exception as e:
                logger.error(f"Booking failed: {e}", exc_info=True)
                messages.error(request, 'Wystąpił błąd podczas zapisywania. Spróbuj ponownie lub zadzwoń.')
                return render(request, 'home.html', {'form': form})
        else:
            logger.warning(f"Form validation failed. Errors: {form.errors}")
            messages.error(request, 'Proszę poprawić błędy w formularzu.')
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

def diagnoza_adhd(request):
    form = AppointmentForm()
    return render(request, 'diagnoza_adhd.html', {'form': form})

def diagnoza_autyzmu(request):
    form = AppointmentForm()
    return render(request, 'diagnoza_autyzmu.html', {'form': form})

def wsparcie_online(request):
    form = AppointmentForm()
    return render(request, 'wsparcie_online.html', {'form': form})

def konsultacje(request):
    form = AppointmentForm()
    return render(request, 'konsultacje.html', {'form': form})

def tus(request):
    form = AppointmentForm()
    return render(request, 'tus.html', {'form': form})

def terapia_indywidualna(request):
    form = AppointmentForm()
    return render(request, 'terapia_indywidualna.html', {'form': form})

def trainings(request):
    form = TrainingInquiryForm()
    return render(request, 'trainings.html', {'form': form})


def _sendTrainingInquiryEmails(name, company, email, phone, subject, message, created_at):
    """Send training inquiry notification to admin in background."""
    try:
        email_configured = (
            settings.EMAIL_HOST and
            settings.EMAIL_HOST.strip() and
            settings.EMAIL_HOST_USER and
            settings.EMAIL_HOST_USER.strip()
        )
        if not email_configured:
            logger.info("Email not configured - skipping training inquiry notification")
            return

        contact_info = []
        if email:
            contact_info.append(f"Email: {email}")
        if phone:
            contact_info.append(f"Telefon: {phone}")

        sendAdminNotification(
            subject=f"Zapytanie szkoleniowe - {company}",
            body=(
                f"NOWE ZAPYTANIE SZKOLENIOWE:\n\n"
                f"Firma: {company}\n"
                f"Osoba kontaktowa: {name}\n"
                f"{chr(10).join(contact_info)}\n"
                f"Temat: {subject}\n"
                f"Data zgłoszenia: {created_at}\n"
                f"\nWiadomość:\n{message or '(brak)'}\n\n"
                f"Skontaktuj się z klientem w ciągu 24h."
            ),
        )

        # Send confirmation to client if email provided
        if email:
            send_mail(
                subject="Potwierdzenie zapytania szkoleniowego - Spektrum Umysłu",
                message=(
                    f"Szanowni Państwo,\n\n"
                    f"Dziękujemy za zainteresowanie naszą ofertą szkoleniową.\n\n"
                    f"Szczegóły zapytania:\n"
                    f"- Firma: {company}\n"
                    f"- Temat: {subject}\n\n"
                    f"Skontaktujemy się z Państwem w ciągu 24 godzin.\n\n"
                    f"W razie pytań prosimy o kontakt:\n"
                    f"- Telefon: +48 606 841 722\n"
                    f"- Email: {settings.EMAIL_FROM}\n\n"
                    f"Z poważaniem,\nSpektrum Umysłu"
                ),
                from_email=settings.EMAIL_FROM,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info("Training inquiry confirmation sent to %s", email)

        logger.info("Training inquiry admin notification sent")
    except Exception as exc:
        logger.error("Training inquiry email failed: %s", exc)


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def training_inquiry(request):
    if request.method == "POST":
        logger.info("Training inquiry form submitted")
        form = TrainingInquiryForm(request.POST)

        if form.is_valid():
            logger.info("Training inquiry form is valid")
            try:
                inquiry = form.save(commit=False)
                inquiry.data_processing_consent = form.cleaned_data.get("data_processing_consent", False)
                inquiry.save()
                logger.info(f"Training inquiry saved: ID {inquiry.id}")

                subject_label = dict(TrainingInquiry.SUBJECT_CHOICES).get(
                    inquiry.subject, inquiry.subject
                )

                thread = threading.Thread(
                    target=_sendTrainingInquiryEmails,
                    kwargs={
                        "name": inquiry.name,
                        "company": inquiry.company,
                        "email": inquiry.email or "",
                        "phone": inquiry.phone or "",
                        "subject": subject_label,
                        "message": inquiry.message,
                        "created_at": inquiry.created_at.strftime("%d.%m.%Y %H:%M"),
                    },
                    daemon=True,
                )
                thread.start()

                messages.success(request, "Dziękujemy! Twoje zapytanie zostało wysłane. Skontaktujemy się w ciągu 24h.")
                return redirect("thanks")

            except Exception as e:
                logger.error(f"Training inquiry failed: {e}", exc_info=True)
                messages.error(request, "Wystąpił błąd podczas zapisywania. Spróbuj ponownie lub zadzwoń.")
                return render(request, "trainings.html", {"form": form})
        else:
            logger.warning(f"Training inquiry validation failed. Errors: {form.errors}")
            messages.error(request, "Proszę poprawić błędy w formularzu.")
            return render(request, "trainings.html", {"form": form})
    return redirect("trainings")

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

@ratelimit(key='ip', rate='3/m', method='POST', block=True)
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
                email_configured = (
                    settings.EMAIL_HOST and
                    settings.EMAIL_HOST.strip() and
                    settings.EMAIL_HOST_USER and
                    settings.EMAIL_HOST_USER.strip()
                )

                if email_configured:
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
                        fail_silently=False,
                    )
                    
                    # Send notification to admin
                    sendAdminNotification(
                        subject=f"Nowe żądanie RODO - {dsr_request.tracking_number}",
                        body=(
                            f"Otrzymano nowe żądanie RODO:\n\n"
                            f"Numer: {dsr_request.tracking_number}\n"
                            f"Rodzaj: {dsr_request.get_request_type_display()}\n"
                            f"Osoba: {dsr_request.full_name}\n"
                            f"Email: {dsr_request.email}\n"
                            f"Telefon: {dsr_request.phone or 'Nie podano'}\n\n"
                            f"Szczegóły w panelu administracyjnym."
                        ),
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
    """Health check endpoint — returns only ok/error, no internal details."""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return HttpResponse("ok", content_type="text/plain", status=200)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HttpResponse("error", content_type="text/plain", status=500)

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
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
