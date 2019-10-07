import logging
import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection

from utils.captcha.captcha import captcha
from utils.res_code import json_response, Code, error_map
from django.views import View
from .forms import CheckImagForm
from apps.verification import constants
from user.models import User
# from utils.yuntongxun.sms import CCP

from django.views.decorators.csrf import csrf_exempt
from utils.yuntongxun.sms import CCP

# 生成日志
logger = logging.getLogger('django')


# Create your views here.
def iamge_code_view(request):
    '''生成验证码
    url:/image_code/
    :param request
    :return'''
    # 1.生成一个验证码，随机字符串生产图片
    text, image = captcha.generate_captcha()
    # 2.在后端保存验证码
    # 保存在session中
    request.session['image_code'] = text
    # 过期时间,session的过期时间
    request.session.set_expiry(constants.IMAGE_CODE_EXPIRES)

    # 3记录一个日志,日志器
    logger.info('Image code:{}'.format(text))

    # 4返回一个图片
    return HttpResponse(content=image, content_type='image/jpg')


# 检查用户名
def check_username_views(requst, username):
    """检查用户名
    url:username/(?P<username>\w{5,10})/"""
    # 去数据库校验数据
    # data = {'errno': '0', 'errmsg': 'ok', 'data':
    #     {'username': username,  # 查用户名
    #      'count': User.objects.filter(username=username).count()#用户查询的数量
    #      }}
    # return JsonResponse(data=data)

    data = {'username': username,  # 查用户名

            'count': User.objects.filter(username=username).count()  # 用户查询的数量
            }
    return json_response(data=data)


def check_mobile_views(requst, mobile):
    """检查用户名
    url:username/(?P<moblie>^(?:+?86)?1(?:3d{3}|5[^4D]d{2}|8d{3}|7(?:[01356789]d{2}|4(?:0d|1[0-2]|9d))|9[189]d{2}|6[567]d{2}|4[579]d{2})d{6}$)/"""
    # 去数据库校验数据
    data = {'mobile': mobile,  # 查用户名
         'count': User.objects.filter(mobile=mobile).count()  # 用户查询的数量
         }
    return json_response(data=data)


class SmsCodeView(View):
    """
       发送短信验证码
       POST /sms_codes/
       """

    def post(self, request):
        # 1.校验参数

        form = CheckImagForm(request.POST, request=request)
        if form.is_valid():
            pass

            # 2.获取手机
            mobile = form.cleaned_data.get('mobile')
            # 3.生成手机验证码
            sms_code = ''.join([random.choice('0123456789') for _ in range(constants.SMS_CODE_LENGTH)])
            print('sms_code%s'%sms_code)
            logger.info('发送短信验证码[正常][mobile: %s sms_code: %s]' % (mobile, sms_code))
            # 4.发送手机验证码
            # ccp = CCP()
            # try:
            #     res = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRES], "1")
            #     if res == 0:
            #         logger.info('发送短信验证码[正常][mobile: %s sms_code: %s]' % (mobile, sms_code))
            #     else:
            #         logger.error('发送短信验证码[失败][moblie: %s sms_code: %s]' % (mobile, sms_code))
            #         return json_response(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # except Exception as e:
            #     logger.error('发送短信验证码[异常][mobile: %s message: %s]' % (mobile, e))
            #     return json_response(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])

            # 5.保存到redis数据库
            # 创建短信验证码发送记录
            redis_coon=get_redis_connection(alias='verify_code')
            sms_flag_key = 'sms_flag_{}'.format(mobile)
            # 创建短信验证码内容记录
            sms_text_key = 'sms_text_{}'.format(mobile)
            pl=redis_coon.pipeline()
            try:
                pl.setex(sms_flag_key,constants.SMS_CODE_INTERVAL,1)
                pl.setex(sms_text_key,constants.SMS_CODE_EXPIRES*60,sms_code)
                pl.execute()
                return json_response(errmsg="短信验证码发送成功！")
            except Exception as e:
                logger.error('redis 执行异常：{}'.format(e))

                return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])


            # 4.发送手机验证码
            # ccp = CCP()
            # try:
            #     res = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRES], "1")
            #     if res == 0:
            #         logger.info('发送短信验证码[正常][mobile: %s sms_code: %s]' % (mobile, sms_code))
            #     else:
            #         logger.error('发送短信验证码[失败][moblie: %s sms_code: %s]' % (mobile, sms_code))
            #         return json_response(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # except Exception as e:
            #     logger.error('发送短信验证码[异常][mobile: %s message: %s]' % (mobile, e))
            #     return json_response(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])

            # 5.保存到redis数据库
            # 创建短信验证码发送记录
            # sms_flag_key = 'sms_flag_{}'.format(mobile)
            # # 创建短信验证码内容记录
            # sms_text_key = 'sms_text_{}'.format(mobile)
            # return json_response(errmsg="短信验证码发送成功！")

            # redis_conn = get_redis_connection(alias='verify_code')
            # # try:
            # pl = redis_conn.pipeline()
            # pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
            # pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
            # pl.execute()
            # return json_response(errmsg="短信验证码发送成功！")


            # redis_conn.set(sms_flag_key, constants.SMS_CODE_INTERVAL, 1)
            # redis_conn.set(sms_text_key, constants.SMS_CODE_EXPIRES * 60, sms_code)

            # except Exception as e:
            #     logger.error('redis 执行异常：{}'.format(e))
            #
            #     return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
            # pl = redis_conn.pipeline()
            #
            # # try:
            # pl.setex(sms_flag_key, constants.SMS_CODE_INTERVAL, 1)
            # pl.setex(sms_text_key, constants.SMS_CODE_EXPIRES * 60, sms_code)
            # # 让管道通知redis执行命令
            # pl.execute()

            # except Exception as e:
            #     logger.error('redis 执行异常：{}'.format(e))
            #
            #     return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        else:
            # 将表单的报错信息进行拼接
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return json_response(errno=Code.PARAMERR, errmsg=err_msg_str)