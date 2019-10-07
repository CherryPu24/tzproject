from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.http import QueryDict
from django.shortcuts import render
from django.views import View
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from .forms import MenuModelForm, GroupModeForm
from utils.res_code import json_response, Code
from .models import Menu
from user.models import User
from .forms import UserModelForm

# Create your views here.


from . import models


class IndexView(View):
    def get(self, request):
        # 通过用户，通过权限，去获取这个列表
        menus = [
            {
                "name": "工作台",
                "url": "myadmin:home",
                "icon": "fa-desktop"
            },
            {
                "name": "新闻管理",
                "icon": "fa-newspaper-o",
                "children": [
                    {
                        "name": "新闻标签管理",
                        "url": "myadmin:wait"
                    }, {
                        "name": "新闻管理",
                        "url": "myadmin:wait"
                    }, {
                        "name": "热门新闻管理",
                        "url": "myadmin:wait"
                    }
                ]
            },
            {
                "name": "轮播图管理",
                "icon": "fa-picture-o",
                "url": "myadmin:wait"
            },
            {
                "name": "文档管理",
                "icon": "fa-folder",
                "url": "myadmin:home"
            },
            {
                "name": "在线课堂",
                "icon": "fa-book",
                "children": [
                    {
                        "name": "课程分类管理",
                        "url": "myadmin:wait"
                    },
                    {
                        "name": "课程管理",
                        "url": "myadmin:wait"
                    },
                    {
                        "name": "讲师管理",
                        "url": "myadmin:wait"
                    }
                ]
            },
            {
                "name": "系统设置",
                "icon": "fa-cogs",
                "children": [
                    {
                        "name": "权限管理",
                        "url": "myadmin:wait"
                    },
                    {
                        "name": "用户管理",
                        "url": "myadmin:wait"
                    },
                    {
                        "name": "菜单管理",
                        "url": "myadmin:menu_list"
                    },
                    {
                        "name": "个人信息",
                        "url": "myadmin:wait"
                    }
                ]
            }

        ]
        # 1. 拿到所有的可用，可见菜单，一级菜单
        objs = Menu.objects.only('name', 'url', 'icon', 'permission__codename',
                                 'permission__content_type__app_label').select_related(
            'permission__content_type').filter(is_delete=False, is_visible=True, parent=None)
        # 2. 过滤用户拥有权限的菜单
        has_permissions = request.user.get_all_permissions()
        # 3. 构造数据结构
        menus = []
        for menu in objs:
            if '%s.%s' % (menu.permission.content_type.app_label, menu.permission.codename) in has_permissions:
                temp = {
                    'name': menu.name,
                    'icon': menu.icon,

                }
                # 检查是否有可用，可见的子菜单
                children = menu.children.filter(is_delete=False, is_visible=True)
                if children:
                    temp['children'] = []
                    for child in children:
                        # if '%s.%s' % (child.permission.content_type.app_label, child.permission.codename) in has_permissions:
                        if '%s.%s' % (child.permission.content_type.app_label, child.permission.codename) in has_permissions:
                            temp['children'].append({
                                'name': child.name,
                                'url': child.url
                            })
                else:
                    if not menu.url:
                        continue
                    temp['url'] = menu.url

                menus.append(temp)
        return render(request, 'myadmin/index.html', context={'menus': menus})


class HomeView(View):
    """
    工作台视图
    """

    def get(self, request):
        return render(request, 'myadmin/home.html')


class WaitView(View):
    """
    未上线功能提示
    """

    def get(self, request):
        return render(request, 'myadmin/wait.html')


class MenuListView(View):
    ''' 菜单列表视图
    url:/admin/menus/
    '''

    def get(self, request):
        menus = models.Menu.objects.only \
            ('name', 'url', 'icon', 'is_visible', 'order', 'codename'). \
            filter(is_delete=False, parent=None)
        return render(request, 'myadmin/menu/meu_list.html', context={'menus': menus})


class MenuAddView(View):
    def get(self, request):
        form = MenuModelForm()
        return render(request, 'myadmin/menu/add_menu.html', context={'form': form})

    def post(self, request):
        form = MenuModelForm(request.POST)

        if form.is_valid():
            # 创建菜单
            new_menu = form.save()
            # 内容对象

            content_type = ContentType.objects.filter(app_label='myadmin', model='menu').first()
            # 菜单权限对象
            permission = Permission.objects.create(name=new_menu.name, content_type=content_type,
                                                   codename=new_menu.codename)
            new_menu.permission = permission
            new_menu.save(update_fields=['permission'])
            return json_response(errmsg='菜单添加成功！')
        else:
            return render(request, 'myadmin/menu/add_menu.html', context={'form': form})


class MenuUpdateView(View):
    def get(self, request, menu_id):
        menu = Menu.objects.filter(id=menu_id).first()
        form = MenuModelForm(instance=menu)
        return render(request, 'myadmin/menu/update_menu.html', context={'form': form})

    """
        菜单管理视图
        url:/admin/menu/<int:menu_id>/
        """

    def delete(self, request, menu_id):
        menu = Menu.objects.filter(id=menu_id).only('name')
        if menu:
            menu = menu[0]
            if menu.children.filter(is_delete=False).exists():
                return json_response(errno=Code.DATAERR, errmsg='父菜单不能被删除')
            menu.permission.delete()
            menu.delete()
            return json_response(errmsg='删除菜单：%s成功' % menu.name)
        else:
            return json_response(errno=Code.NODATA, errmsg='菜单不存在！')
        """
           菜单管理视图
           url:/admin/menu/<int:menu_id>/
           """

    def put(self, request, menu_id):
        menu = Menu.objects.filter(id=menu_id).first()
        # 获取put参数
        put_data = QueryDict(request.body)
        form = MenuModelForm(put_data, instance=menu)
        if form.is_valid:
            obj = form.save()
            flag = False
            # 检查修改字段是否与权限有关
            if 'name' in form.changed_data:
                obj.permission.name = obj.name
                flag = True
            if 'codename' in form.changed_data:
                obj.permission.codename = obj.name
                flag = True

            if flag:
                obj.permission.save()
            return json_response(errmsg='菜单修改成功！')
        else:
            return render(request, 'admin/menu/update_menu.html', context={'form': form})


class UserListView(View):
    def get(self, request):
        # 1.获取查询集
        user_query = User.objects.only('username', 'is_active', 'mobile', 'is_staff', 'is_superuser')

        # 2.接收参数并检验
        # 3.过滤
        # 4.分页

        # 5.渲染模板
        # 6.返回
        user_queryset = User.objects.only('username', 'is_active', 'mobile', 'is_staff', 'is_superuser')
        groups = Group.objects.only('name').all()
        query_dict = {}
        # 检索
        groups__id = request.GET.get('group')
        if groups__id:
            try:
                group_id = int(groups__id)
                query_dict['groups__id'] = groups__id
            except Exception as e:
                pass

        is_staff = request.GET.get('is_staff')
        if is_staff == '0':
            query_dict['is_staff'] = False
        if is_staff == '1':
            query_dict['is_staff'] = True

        is_superuser = request.GET.get('is_superuser')
        if is_superuser == '0':
            query_dict['is_superuser'] = False
        if is_superuser == '1':
            query_dict['is_superuser'] = True

        username = request.GET.get('username')

        if username:
            query_dict['username'] = username

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            page = 1

        paginater = Paginator(user_queryset.filter(**query_dict), 2)

        users = paginater.get_page(page)
        context = {
            'users': users,
            'groups': groups
        }
        context.update(query_dict)
        return render(request, 'myadmin/user/user_list.html', context=context)


class UserUpdateView(View):
    """
       用户更新视图
       url:/admin/user/<int:user_id>
       """

    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if user:
            form = UserModelForm(instance=user)
        else:
            form = UserModelForm()
        return render(request, 'myadmin/user/user_detail.html', context={'form': form})

    # 用户修改的后台
    def put(self, request, user_id):
        # 1.拿到要修改的用户对象
        # 2拿到前端传递的数据
        # 4.如果成功保存数据
        # 5.不存在，返回错误
        user = User.objects.filter(id=user_id).first()
        if not user:
            return json_response(errno=Code.NODATA, errmsg='此用户不存在')

        put_data = QueryDict(request.body)
        # 创建表单对象、
        form = UserModelForm(put_data, instance=user)
        if form.is_valid():
            form.save()
            return json_response(errmsg='用户修改成功')
        else:
            return render(request, 'myadmin/user/user_detail.html', context={'form': form})


class GroupListView(View):
    def get(self, request):
        # 1.拿到分组的查询集
        # 2.渲染
        groups = Group.objects.only('name').all()
        return render(request, 'myadmin/group/group_list.html', context={'groups': groups})


class GroupUpdateView(View):
    def get(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if group:
            form = GroupModeForm(instance=group)
            permissions = group.permissions.only('id').all()
        else:
            form = GroupModeForm()
            permissions = []
        menus = Menu.objects.only('name', 'permission_id').select_related('permission').filter(is_delete=False,
                                                                                               parent=None)
        print(form, menus, permissions)
        return render(request, 'myadmin/group/group_detail.html', context={
            'form': form,
            'menus': menus,
            'permissions': permissions
        })
