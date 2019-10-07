﻿$(function () {
    // 定义状态变量
    let isUsernameReady = false,
        isPasswordReady = false,
        isMobileReady = false;

    // 1.点击刷新图像验证码
    let $img = $('.form-contain .form-item .captcha-graph-img img');


    $img.click(function () {
        $img.attr('src', '/image_code/?rand=' + Math.random())
    });

    // 2.鼠标离开用户名输入框校验用户名
    let $username = $('#username');
    $username.blur(fnCheckUsername);

    function fnCheckUsername () {
        isUsernameReady = false;
        let sUsername = $username.val();    //获取用户字符串
        if (sUsername === ''){
            message.showError('用户名不能为空！');
            return
        }
        if (!(/^\w{5,20}$/).test(sUsername)){
            message.showError('请输入5-20个字符的用户名');
            return
        }
        $.ajax({
            url: '/username/' + sUsername + '/',
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                if(data.data.count !== 0){
                    message.showError(data.data.username + '已经注册，请重新输入！')
                }else {
                    message.showInfo(data.data.username + '可以正常使用！')
                    isUsernameReady = true
                }
            },
            error: function (xhr, msg) {
                message.showError('服务器超时，请重试！')
            }
        });
    }

    // 3.检测密码是否一致
    let $passwordRepeat = $('input[name="password_repeat"]');
    $passwordRepeat.blur(fnCheckPassword);

    function fnCheckPassword () {
        isPasswordReady = false;
        let password = $('input[name="password"]').val();
        let passwordRepeat = $passwordRepeat.val();
        if (password === '' || passwordRepeat === ''){
            message.showError('密码不能为空');
            return
        }
        if (password !== passwordRepeat){
            message.showError('两次密码输入不一致');
            return
        }
        if (password === passwordRepeat){
            isPasswordReady = true
        }
    }

    // 4.检查手机号码是否可用
    let $mobile = $('input[name="telephone"]');
    $mobile.blur(fnCheckMobile);

    function fnCheckMobile () {
        isMobileReady = true;
        let sMobile = $mobile.val();
        if(sMobile === ''){
            message.showError('手机号码不能为空');
            return
        }
        if(!(/^1[3-9]\d{9}$/).test(sMobile)){
            message.showError('手机号码格式不正确');
            return
        }

        $.ajax({
            url: '/mobile/' + sMobile + '/',
            type: 'GET',
            dataType: 'json',
            success: function (res) {
                if(res.data.count !== 0){
                    message.showError(res.data.mobile + '已经注册，请重新输入！')
                }else {
                    message.showInfo(res.data.mobile + '可以正常使用！');
                    isMobileReady = true
                }
            },
            error: function (xhr, msg) {
                message.showError('服务器超时，请重试！')
            }
        });

    }


    // 5.发送手机验证码
    let $smsButton = $('.sms-captcha');
    $smsButton.click(function () {
        let sCaptcha = $('input[name="captcha_graph"]').val();
        if(sCaptcha === ''){
            message.showError('请输入验证码');
            return
        }
        if(!isMobileReady){
            fnCheckMobile();
            return
        }

        $.ajax({
            url: '/sms_code/',
            type: 'POST',
            data: {
                mobile: $mobile.val(),
                captcha: sCaptcha
            },
            dataType: 'json',
            success: function (data) {
                if(data.errno !== '0'){
                    message.showError(data.errmsg)
                }else {
                    message.showSuccess(data.errmsg);
                    //设置禁用
                    $smsButton.attr('disable',true)

                    var num = 60;
                    //设置计时器
                    let t = setInterval(function () {
                        $smsButton.html('倒计时'+num+'秒');
                        if(num===1){
                            clearInterval(t)
                            $smsButton.removeAttr('disable')
                            $smsButton.html('获取短信验证码')
                        }
                       num--;
                    },1000)
                }
            },
            error: function (xhr, msg) {
                message.showError('服务器超时，请重试！')
            }
        });

    });

    // 6.注册
    let $submitBtn = $('.register-btn');
    $submitBtn.click(function (e) {
        //阻止默认提交
        e.preventDefault();
        // 1.检查用户名
        if(!isUsernameReady){
            fnCheckUsername();
            return
        }
        // 2.检查密码
        if(!isPasswordReady){
            fnCheckPassword();
            return
        }
        // 3.检查电话号码
        if(!isMobileReady){
            fnCheckMobile();
            return
        }
        // 4.检查短信验证码
        let sSmsCode = $('input[name="sms_captcha"]').val();
        if(sSmsCode === ''){
            message.showError('短信验证码不能为空！');
            return
        }
        if(!(/^\d{4}$/).test(sSmsCode)){
            message.showError('短信验证码长度不正确，必须是4位数字！');
            return
        }

        $.ajax({
            url: '/user/register/',
            type: 'POST',
            data:{
                username: $username.val(),
                password: $('input[name="password"]').val(),
                password_repeat: $passwordRepeat.val(),
                mobile: $mobile.val(),
                sms_code: sSmsCode
            },
            dataType: 'json',
            success: function (res) {
                if(res.errno === '0'){
                    message.showSuccess('恭喜您，注册成功!');
                    setTimeout(function () {
                        //注册成功3秒后重定向到登录页面
                        window.location.href = '/user/login/'
                    }, 3000)
                }else{
                    //注册失败
                    message.showError(res.errmsg)
                }
            },
            error: function () {
                message.showError('服务器超时，请重试！')
            }
        })

    });
});