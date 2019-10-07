from django.urls import path,re_path


from . import views

app_name='verification'
urlpatterns=[path('image_code/',views.iamge_code_view,name='image_code'),
             re_path('username/(?P<username>\w{5,10})/',views.check_username_views,name= 'check'),
             re_path('mobile/(?P<mobile>1[3-9]\d{9})/',views.check_mobile_views,name= 'mobile'),
             path('sms_code/',views.SmsCodeView.as_view(),name='sms_code')

             ]