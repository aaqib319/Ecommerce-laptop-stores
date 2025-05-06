from django import template

register = template.Library()

@register.filter
def unique(queryset, attr):
    """Returns unique values for a given attribute from a queryset."""
    seen = set()
    unique_items = []
    
    for item in queryset:
        value = getattr(item, attr, None)
        if value not in seen:
            seen.add(value)
            unique_items.append(item)
    
    return unique_items

from django import template

register = template.Library()

@register.filter
def unique(queryset, field_name):
    """Returns unique values for a given field in a queryset."""
    unique_values = set(getattr(obj, field_name) for obj in queryset)
    return unique_values