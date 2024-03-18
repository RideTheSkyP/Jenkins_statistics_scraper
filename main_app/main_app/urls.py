from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.urls import include, path
from django.conf.urls.static import static
# from rest_api import urls as api_urls


app_name = 'main_app'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('jenkins_statistics.urls', namespace='statistics')),
    # path('api/', include(api_urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
