# cryptonovaproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Core app handles the homepage ('') and other base routes
    path('', include('core.urls', namespace='core')),
    # Include URLs from other apps with prefixes
    path('markets/', include('markets.urls', namespace='markets')),
    path('coin/', include(('markets.urls', 'markets'), namespace='coin')),  
    path('portfolio/', include('portfolio.urls', namespace='portfolio')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('learn/', include('learn.urls', namespace='learn')),
]

