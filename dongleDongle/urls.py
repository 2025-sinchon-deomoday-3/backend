from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('rates/', include('rates.urls')),
    path('ledgers/', include('ledgers.urls')),
    path('budgets/', include('budgets.urls')),
    path('summaries/', include('summaries.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)