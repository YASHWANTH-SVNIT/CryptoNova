# core/urls.py
from django.urls import path
from . import views

app_name = 'core' # Namespace for this app's URLs

urlpatterns = [
    # The homepage
    path('', views.index_view, name='index'),
    # Placeholder simple pages (using a generic view for now)
    path('about/', views.placeholder_view, name='about', kwargs={'page_name': 'About Us'}),
    path('privacy/', views.placeholder_view, name='privacy', kwargs={'page_name': 'Privacy Policy'}),
    path('terms/', views.placeholder_view, name='terms', kwargs={'page_name': 'Terms of Service'}),
    path('contact/', views.placeholder_view, name='contact', kwargs={'page_name': 'Contact Us'}),

    # Maybe API endpoints for fetching chart data if not done directly in page view
    path('api/market-chart-data/', views.market_chart_data_api, name='market_chart_data_api'),
]

