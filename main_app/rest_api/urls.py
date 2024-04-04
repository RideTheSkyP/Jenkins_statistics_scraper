from django.urls import path

from . import views

app_name = 'rest_api'
urlpatterns = [
    path('pipelines/', views.PipelineListApiView.as_view()),
    path('pipelines/<int:pipeline>', views.PipelineDetailApiView.as_view()),
    path('pipelines/<str:pipeline>', views.PipelineDetailApiView.as_view()),
    path('jobs/', views.JobListApiView.as_view()),
    path('jobs/<int:job>', views.JobDetailApiView.as_view()),
    path('jobs/<str:job>', views.JobDetailApiView.as_view()),
    path('builds/', views.BuildListApiView.as_view()),
    path('builds/<int:build_id>', views.BuildDetailApiView.as_view()),
    path('job_results/', views.JobResultListApiView.as_view()),
    path('job_results/<int:job_result>', views.JobResultDetailApiView.as_view()),
    path('job_results/<str:job_result>', views.JobResultDetailApiView.as_view())
]
