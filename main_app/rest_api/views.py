from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.urls import include, path, re_path
from django.conf.urls.static import static

from . import views

app_name = 'rest_api'
urlpatterns = [
    path('', views.index, name='index'),
]
