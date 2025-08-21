from django import template

register = template.Library()

@register.filter
def humanize_views(value):
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        return str(value)
    except:
        return value
