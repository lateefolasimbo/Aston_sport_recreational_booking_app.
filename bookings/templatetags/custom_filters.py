from django import template
from datetime import date

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def subtract(value, arg):
    if isinstance(value, date) and isinstance(arg, date):
        return (value - arg).days  # Get only the number of days
    return ''