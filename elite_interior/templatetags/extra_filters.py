from django import template

register = template.Library()

@register.filter(name='length_is')
def length_is(value, expected_length):
    try:
        return len(value) == int(expected_length)
    except:
        return False
