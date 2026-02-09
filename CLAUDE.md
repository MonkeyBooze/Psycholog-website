# CLAUDE.md

This file provides guidance to Claude Code and Gemini Agent when working with code in this repository.

## Project Overview
**Project Name:** Spektrum Umysłu (Psychology Practice)
**Domain:** Healthcare / Psychology / GDPR (RODO)
**Region:** Poland (pl-pl, Europe/Warsaw)
**Language:** Code in English, User-facing strings in Polish.

**Technology Stack:**
- **Backend:** Django 4.2+, Python 3.10+
- **Frontend:** Tailwind CSS (via CDN for dev, npm/PostCSS for prod), HTML5 Templates
- **Database:** PostgreSQL (Prod), SQLite (Dev)
- **Server:** Gunicorn, WhiteNoise (Static files)
- **Config:** django-environ

## Coding Standards & Guidelines

### Python (Backend)
- **Style:** Follow PEP8 strictly.
- **Type Hinting:** Use `typing` module for ALL function arguments and return values.
- **Strings:** Use f-strings (`f"{var}"`) exclusively.
- **Imports:** Sort: Standard Lib -> Third Party (Django) -> Local Apps.
- **Paths:** Use `pathlib.Path` objects, never `os.path.join`.
- **Safety:** Always validate permissions (`UserPassesTestMixin`, `@login_required`) for views.

### Frontend (Tailwind CSS)
- **Class Ordering:** Group utility classes logically (Layout -> Spacing -> Typography -> Color).
- **Responsive:** Mobile-first approach (`class="..."` is mobile, `md:...` is desktop).
  - All grids collapse to single column on mobile.
  - CTAs become full-width on mobile.
- **Components:** Avoid raw CSS. Use Tailwind utility classes for everything.
- **Colors:** Use project palette in css/style.css

#### Typography
- **Font Families:** Keep existing font families. Do not change fonts.
- **Sizes/Weights:** Adjust sizes and weights as specified per section/design.

#### Animations
- **Fade-in-on-scroll:** Add subtle fade-in effect to all major sections.
  - Staggered timing: ~200ms delay between elements.
  - Use CSS transitions only. No heavy JS animation libraries.

#### Icons
- **Icon Set:** Use a consistent icon set (Lucide, Heroicons, or whatever is already in the project).
- **No Emoji:** Do not use emoji as icons in production code.

#### ZnanyLekarz Badge
- **Position:** Sticky floating element (bottom-right or top-right corner).
- **Content:** "⭐ 4.9/5 · ZnanyLekarz" (clickable, links to ZnanyLekarz profile).
- **Colors:**
  - Background: `var(--bright-gray)`
  - Text: `var(--mystic)`
  - Star: `var(--spring-green)`
- **Behavior:** Subtle, not obstructive. Hide on mobile or make smaller.
- **Visibility:** Should appear on all pages.

## Testing Strategy
- **Runner:** `pytest` (preferred) or `django.test`.
- **Rules:**
  1. Mock all external calls (Email, Google Analytics).
  2. Use `Factory Boy` for model instantiation if available.
  3. Test both "Happy Path" and "Error Cases" (e.g., form validation failure).
  4. **GDPR Check:** Verify that personal data is never logged to console/files during tests.

## Development Commands

### Setup & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start Dev Server
python manage.py runserver

# Tailwind (if using standalone watcher)
npm run dev