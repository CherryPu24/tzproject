from  django.urls import path
from . import views
app_name='myadmin'
urlpatterns=[path('',views.IndexView.as_view(),name='index'),
             path('home/', views.HomeView.as_view(), name='home'),
             path('wait/', views.WaitView.as_view(), name='wait'),
             path('menus/',views.MenuListView.as_view(),name='menu_list'),
             path('menu/',views.MenuAddView.as_view(),name='add_menu'),
             path('menu/<int:menu_id>/',views.MenuUpdateView.as_view(),name='menu_manage'),
             path('users/',views.UserListView.as_view(),name='user_list'),
             path('user/<int:user_id>/',views.UserUpdateView.as_view(),name='user_update'),
             path('groups/',views.GroupListView.as_view(),name='group_list'),
             path('group/<int:group_id>/',views.GroupUpdateView.as_view(),name='group_update')


             ]