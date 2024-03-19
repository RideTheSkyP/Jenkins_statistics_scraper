from django.conf import settings
from django.views.static import serve
from django.urls import include, path, re_path
from django.conf.urls.static import static

from . import views

app_name = 'jenkins_statistics'
urlpatterns = [
    path('', views.index, name='index'),
    path('test_results', views.test_results, name='test_results'),
    path('test_failures', views.test_failures, name='test_failures'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
