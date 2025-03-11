from django.urls import path, include
from core.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/', include('api.urls')),
]