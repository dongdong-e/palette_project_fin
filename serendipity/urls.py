from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main_page import views

urlpatterns = [
    path('main/', include('main_page.urls')),
    path('account/', include('account.urls')),
    path('admin/', admin.site.urls),
    path('', views.main),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)