from django.urls import path

from . import views

app_name='news'
urlpatterns=[path('',views.index,name='index'),
             path('news/',views.NewslistView.as_view(),name='new_list'),
             path('news/banners/',views.NewsBannerView.as_view(),name='news_banner'),
             path('news/<int:news_id>/',views.NewsDetailView.as_view(),name='news_detail'),
             path('news/<int:news_id>/comment/', views.NewsCommentsViews.as_view(), name='news_comment'),
             path('news/search/',views.NewsSearchView.as_view(),name='news_search')]