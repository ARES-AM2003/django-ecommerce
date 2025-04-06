from django import template

register = template.Library()

@register.simple_tag
def increment_var(value):
    """Increments a variable."""
    return value + 1
