#marksets/urls.py
from django.urls import path
from . import views

app_name = 'markets'

urlpatterns = [
    path('', views.market_list_view, name='list'),
    path('<str:coin_id>/', views.coin_detail_view, name='detail'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
]