import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Whitelist of tags allowed — covers rich-text editor output + inline SVG icons
ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'div', 'em',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
    'li', 'ol', 'p', 'pre', 'span', 'strong', 'table', 'tbody',
    'td', 'th', 'thead', 'tr', 'u', 'ul', 'figure', 'figcaption',
    'sup', 'sub', 'small',
    # SVG elements used in service icons
    'svg', 'path', 'circle', 'polyline', 'line', 'rect', 'g',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'loading'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
    'div': ['class'],
    'span': ['class'],
    'p': ['class'],
    'figure': ['class'],
    # SVG presentational attributes
    'svg': ['width', 'height', 'viewbox', 'fill', 'stroke', 'stroke-width', 'xmlns'],
    'path': ['d', 'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin'],
    'circle': ['cx', 'cy', 'r', 'fill', 'stroke', 'stroke-width'],
    'polyline': ['points', 'fill', 'stroke', 'stroke-width'],
    'line': ['x1', 'y1', 'x2', 'y2', 'stroke', 'stroke-width'],
    'rect': ['x', 'y', 'width', 'height', 'rx', 'ry', 'fill', 'stroke'],
    'g': ['transform', 'fill', 'stroke'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


@register.filter(name='sanitize_html')
def sanitize_html(value):
    """Sanitize HTML content, allowing only safe tags and attributes."""
    if not value:
        return ''
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return mark_safe(cleaned)
