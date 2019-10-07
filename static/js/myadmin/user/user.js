  // 用户详情
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
...
// 注意在user_list中在相应的tr中添加data-url的属性
<td style="width: 40px" data-url="{% url 'myadmin:user_update' user.id %}">