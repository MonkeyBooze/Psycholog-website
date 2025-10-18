# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based psychology practice website ("Spektrum Umysłu") with appointment booking, blog functionality, and GDPR compliance features. The site is configured for Polish language (pl-pl) with Europe/Warsaw timezone.

**Technology Stack:**
- Django 4.2+
- WhiteNoise for static file serving
- Gunicorn for production deployment
- PostgreSQL support (via psycopg2-binary)
- SQLite for local development
- django-environ for environment configuration

## Common Development Commands

### Database Management
```bash
# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create superuser for admin access
python manage.py createsuperuser
```

### Static Files
```bash
# Collect static files (required before deployment)
python manage.py collectstatic --noinput
```

### Running the Server
```bash
# Development server
python manage.py runserver

# Production (uses Procfile configuration)
gunicorn project.wsgi --log-file -
```

### Testing
```bash
# Run tests
python manage.py test app

# Run specific test
python manage.py test app.tests.TestClassName
```

## Project Structure

**Settings Module:** `project/` (not "config" or "core")
- Main Django project is in `project/` directory
- Django settings module: `project.settings`
- WSGI application: `project.wsgi`

**Main App:** `app/`
- All business logic, models, views, and templates are in the `app/` application
- Templates directory: `app/templates/`
- Static files directory: `app/static/`

## Architecture & Key Patterns

### Configuration Management
Settings use django-environ for environment variables loaded from `.env` file:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (default: False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE_URL` - Database connection string (optional, defaults to SQLite)
- Email configuration: `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_FROM`
- `GA_MEASUREMENT_ID` - Google Analytics 4 measurement ID
- Security flags: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`

### Models Architecture

**Core Models:**
1. **Appointment** - Appointment booking with GDPR consent tracking
   - Tracks both data processing consent and marketing consent separately
   - Stores consent timestamps for audit trail

2. **DataSubjectRightsRequest** - GDPR data subject rights requests
   - Auto-generates tracking numbers with format `DSR{UUID}`
   - Supports all RODO/GDPR request types (access, rectification, erasure, portability, restriction, objection)
   - Status workflow: pending → in_progress → completed/rejected

3. **BlogPost** - Blog posts with SEO fields
   - Draft/published workflow
   - Auto-generates slug from title
   - Auto-sets published_at on first publish
   - Tracks view counts (incremented on detail view)
   - Supports featured images, meta descriptions, and keywords

4. **BlogCategory** - Blog categorization
   - Auto-generates slug from name

5. **StaffMember** - Team/staff member profiles
   - Supports display ordering
   - Active/inactive status

### Views & Forms Pattern

**Form Security:**
- All user-facing forms include honeypot fields (`hp_field`) for bot prevention
- GDPR consent checkboxes are required and validated at form level
- Forms validate honeypot in `clean()` method

**Email Notifications:**
- Views send dual emails: confirmation to user + notification to admin
- Email sending is wrapped in try/except with `fail_silently=True`
- Check `settings.EMAIL_HOST` before attempting to send

**Blog Functionality:**
- Blog post detail view increments view count using `F('views_count') + 1`
- Pagination set to 6 posts per page
- Search across title, excerpt, content, and meta_keywords
- Category filtering via query parameter

### Template Context

**Custom Context Processor** (`app.context_processors.site_settings`):
Makes these variables available in all templates:
- `GA_MEASUREMENT_ID`
- `SITE_NAME` (hardcoded: "Spektrum Umysłu")
- `PRIMARY_COLOR` (#003366)
- `ACCENT_COLOR` (#006633)

### URL Configuration

**Main Routes:**
- Admin: `/admin/`
- Home: `/`
- Booking: `/book/`
- Contact: `/kontakt/`
- About: `/o-nas/`
- Pricing: `/cennik/`
- Blog: `/blog/`
- Blog post: `/blog/<slug>/`
- Blog category: `/blog/kategoria/<slug>/`
- GDPR request: `/data-subject-rights/`
- Privacy: `/privacy/`
- Cookie policy: `/cookie-policy/`
- Terms: `/terms/`
- Healthcheck: `/health/`

**SEO Features:**
- Sitemap at `/sitemap.xml` (includes static pages and published blog posts)
- Robots.txt at `/robots.txt` served as plain text template

### Static Files Configuration
- Uses WhiteNoise with `CompressedManifestStaticFilesStorage`
- Static files collected to `staticfiles/` directory
- Source static files in `app/static/`
- Django admin static files automatically included

## Important Notes

### GDPR/RODO Compliance
This site implements strict GDPR compliance for a Polish healthcare practice:
- All forms require explicit consent checkboxes
- Consent timestamps are stored for audit
- Data subject rights request system with tracking numbers
- Email notifications include Polish language text

### Database Migrations
Four migrations exist:
1. `0001_initial` - Initial Appointment model
2. `0002_datasubjectrightsrequest` - GDPR request handling
3. `0003_blogcategory_blogpost` - Blog functionality
4. `0004_staffmember` - Team member profiles

### Admin Interface
Customized admin with:
- List filters and search on all models
- Readonly fields for timestamps and auto-generated values
- Fieldsets for organized editing
- Bulk actions for blog posts (publish/draft)
- Prepopulated slug fields