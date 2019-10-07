
from  django.shortcuts import render
from  django.urls import path

from . import views
app_name='doc'

urlpatterns=[path('',views.indexView,name='index'),
             path('docs/', views.DocListView.as_view(), name='doc_list'),
             path('dload/', views.DocDownloadView.as_view())

            ]