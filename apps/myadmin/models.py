from django.contrib.auth.models import Permission
from django.db import models
from utils.models import BaseModel

# Create your models here.
class Menu(BaseModel):
    name=models.CharField('菜单名',max_length=48,help_text='菜单名',unique=True)
    url=models.CharField('url',max_length=256,null=True,blank=True,help_text='url')
    parent=models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='children')
    order=models.SmallIntegerField('排序',default=0)
    permission=models.OneToOneField(Permission,on_delete=models.CASCADE,null=True)
    icon=models.CharField('图标',max_length=48,default='fa-link')
    codename=models.CharField('权限码',max_length=48,help_text='权限码')
    is_visible=models.BooleanField('是否可见',default=False)
    class Meta:
        ordering = ['-order']
        db_table='tb_menu'
        verbose_name='菜单'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name



