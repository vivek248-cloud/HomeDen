from django import template
from elite_interior.models import SEOServicePage

register = template.Library()

@register.simple_tag
def get_seo_pages():
    return SEOServicePage.objects.all()
