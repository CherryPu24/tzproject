from django.contrib.auth import logout
from django.shortcuts import render, redirect,reverse
from django.views import View

from utils.res_code import json_response, Code
from .forms import RegisterForm,LoginForm
from .models import User





# Create your views here.

class LoginView(View):
    def get(self,request):
        return render(request,'user/login.html')
    def post(self,request):
        form=LoginForm(request.POST,request=request)
        if form.is_valid():
            data='恭喜登录成功！'
            return json_response(data=data)
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_msg_str = '/'.join(err_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=err_msg_str)

class LogoutView(View):
    """
       登出视图
       """
    def get(self,request):
        logout(request)
        return redirect(reverse('user:login'))



class RegisterView(View):
    def get(self,request):
        return render(request, 'user/register.html')
    def post(self,request):
        # 1数据校验
        form=RegisterForm(request.POST)
        if form.is_valid():
            # 2创建数据
            print(form.is_valid())
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password')
            mobile=form.cleaned_data.get('mobile')
            #create_user密码自动加密，Django实现

            User.objects.create_user(username=username,mobile=mobile,password=password)
            return json_response(errmsg='恭喜你注册成功')

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_msg_str = '/'.join(err_msg_list)
            return json_response(errno=Code.PARAMER, errmsg=err_msg_str)




