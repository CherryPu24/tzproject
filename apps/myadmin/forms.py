from django import forms
from django.contrib.auth.models import Permission, Group

from user.models import User
from .models import Menu
class MenuModelForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=None, required=False, help_text='父菜单')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Menu.objects.filter(is_delete=False, is_visible=True, parent=None)
        # https://docs.djangoproject.com/en/2.2/ref/forms/fields/#fields-which-handle-relationships

    class Meta:
        model = Menu
        fields = ['name', 'url', 'order', 'parent', 'icon', 'codename', 'is_visible']
class UserModelForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','mobile','is_staff','is_superuser','is_active','groups']
class GroupModeForm(forms.ModelForm):
    permissions=forms.ModelMultipleChoiceField(queryset=None,required=False,help_text='权限',label='权限')
    def __int__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.filter(menu__is_delete=False)
    class Meta:
        model=Group
        fields=['name','permissions']
