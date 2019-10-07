# !/usr/bin/env python
# -*- coding:utf-8 -*-
# author:心蓝 2019/9/9 21:37
from django.template import Library
from django.forms.widgets import CheckboxInput

register = Library()


@register.filter()
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.filter()
def is_url_field(field):
    return True if 'url' in field.label else False
