from django.urls import path
from . import views

app_name = 'learn'

urlpatterns = [
    path('', views.learn_home, name='index'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
]
