$(() => {

    let $queryForm = $('form.user-query');       // 查询表单

    // 分页
    let $pageLi = $('ul.pagination li').not('.active').not('.disabled');

    $pageLi.click(function () {
        let $this = $(this);
        $
            .ajax({
                url: $('.sidebar-menu li.active a').data('url'),
                data: $queryForm.serialize() + '&page=' + $this.data('page'),
                type: 'GET'
            })
            .done((res) => {
                $('#content').html(res)
            })
            .fail(() => {
                message.showError('服务器超时，请重试！')
            })
    });

    // 查询
    let $queryBtn = $('form.user-query button.query');    // 查询按钮
    let $resetBtn = $('form.user-query button.reset');    // 重置按钮

    $queryBtn.click(() => {

        $
            .ajax({
                url: $('.sidebar-menu li.active a').data('url'),
                data: $queryForm.serialize(),
                type: 'GET'
            })
            .done((res) => {
                $('#content').html(res)
            })
            .fail(() => {
                message.showError('服务器超时，请重试！')
            })
    });

    // 重置
    $resetBtn.click(() => {
        // 让表单重置
        $queryForm[0].reset();
        $
            .ajax({
                url: $('.sidebar-menu li.active a').data('url'),
                type: 'GET'
            })
            .done((res) => {
                $('#content').html(res)
            })
            .fail(() => {
                message.showError('服务器超时，请重试！')
            })
    });

    // 用户详情
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

});