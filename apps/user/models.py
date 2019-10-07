from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager as _UserManager

# Create your models here.
class UserManager(_UserManager):
    """自定义管理器"""
    def create_superuser(self, username, password, email=None, **extra_fields):
        return  super().create_superuser(username=username,password=password,email=email,**extra_fields)
class User(AbstractUser):
    """自定义user模型 字段mobile ，email-active"""
    mobile=models.CharField("手机号",max_length=11,help_text="手机",unique=True,error_messages={'unique':'此手机号码已经注册'})
    email_active=models.BooleanField('邮箱状态',default=False)
    class Meta:
        db_table='tb_user'#指定数据表明
        verbose_name='用户'#在admin中显示的名称
        verbose_name_plural=verbose_name#复数
    def __str__(self):
        return self.username
    #通过createsuperuser这个命令创建用户时，需要的字段
    REQUIRED_FIELDS = ['mobile']
    #user模型相当强大，通过usermanager来修改创建超级用户时必须使用email
    objects=UserManager()

