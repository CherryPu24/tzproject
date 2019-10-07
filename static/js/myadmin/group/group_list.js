// 创建 js/myadmin/group/group_list.js
$(()=>{
        // 分组详情
    $('tr').each(function () {
        $(this).children('td:first').click(function () {
            $('#content').load(
                $(this).data('url'),
                (response, status, xhr) => {
                    if (status !== 'success') {
                        message.showError('服务器超时，请重试！')
                    }
                }
            );
        })
    });
});