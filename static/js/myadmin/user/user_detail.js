$(() => {
    // 1. 点击返回
    // 回到用户列表页面，触发点击用户管理菜单
    $('.box-footer button.back').click(() => {
        $('#content').load(
            $('.sidebar-menu li.active a').data('url'),
            (response, status, xhr) => {
                if (status !== 'success') {
                    message.showError('服务器超时，请重试！')
                }
            }
        );
    });
    // 2. 点击修改
    $('.box-footer button.save').click(function () {
        // 发送ajax
        $
            .ajax({
                url: $(this).data('url'),
                data: $('form').serialize(),
                type: 'PUT'
            })
            .done((res) => {
                if (res.errno === '0') {
                    message.showSuccess(res.errmsg);
                    // 跳转到 用户列表
                    $('#content').load(
                        $('.sidebar-menu li.active a').data('url'),
                        (response, status, xhr) => {
                            if (status !== 'success') {
                                message.showError('服务器超时，请重试！')
                            }
                        }
                    );
                }else{
                    // 失败了返回的是渲染了额错误信息的html
                    // 替换原有内容
                    $('#content').html(res)
                }
            })
            .fail(() => {
                message.showError('服务器超时，请重试！')
            })
    });

});