from django.contrib import admin
from django.urls import include, path
from rest_api import urls as api_urls


app_name = 'main_app'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('jenkins_statistics.urls', namespace='statistics')),
    path('api/', include(api_urls))
]
