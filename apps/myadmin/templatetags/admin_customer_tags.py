from django.template import Library
register=Library()
@register.simple_tag
def add_class(field,class_str):
    return field.as_widget(attrs={'class':class_str})
