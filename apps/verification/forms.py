from django import forms
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from user.models import User

# 创建手机号的正则校验器
mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', '手机号码格式不正确')


class CheckImagForm(forms.Form):
    """
    check image code
    """
#拿出request的值
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        #不破坏父类
        super().__init__(*args, **kwargs)

    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={
                                 'max_length': '手机长度有误',
                                 'min_length': '手机长度有误',
                                 'required': '手机号不能为空'
                             })

    captcha = forms.CharField(max_length=4, min_length=4,
                              error_messages={
                                  'max_length': '验证码长度有误',
                                  'min_length': '图形验证码长度有误',
                                  'required': '图形验证码不能为空'
                              })

    def clean(self):
        clean_data = super().clean()
        mobile = clean_data.get('mobile')
        captcha = clean_data.get('captcha')
    # 1.校验图片验证码
        image_code = self.request.session.get('image_code')
        if (not image_code) or (image_code.lower() != captcha.lower()):
            raise forms.ValidationError('图片验证码校验失败！')

    # 2.校验是否在60秒内已发送过短信
        redis_conn = get_redis_connection(alias='verify_code')
        if redis_conn.get('sms_flag_{}'.format(mobile)):
            raise forms.ValidationError('获取短信验证码过于频繁')

    # 3.校验手机号码是否已注册
        if User.objects.filter(mobile=mobile).count():#可以用exist
            raise forms.ValidationError('手机号已注册，请重新输入')