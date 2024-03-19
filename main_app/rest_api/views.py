from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListCreateAPIView

from jenkins_statistics.models import Job, Build, JobResults
from .serializers import JobSerializer, BuildSerializer, JobResultsSerializer


class JobListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobSerializer

    def post(self, request, *args, **kwargs):
        data = {'job_name': request.data.get('job_name')}
        serializer = JobSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Job.objects.all()
        job_id = self.request.query_params.get('id')
        job_name = self.request.query_params.get('job_name')
        if job_id is not None:
            queryset = queryset.filter(id=job_id)
        if job_name is not None:
            queryset = queryset.filter(job_name=job_name)
        return queryset


class JobDetailApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, job):
        try:
            if isinstance(job, int):
                return Job.objects.get(id=job)
            elif isinstance(job, str):
                return Job.objects.get(job_name=job)
        except Job.DoesNotExist:
            return None

    def get(self, request, job, *args, **kwargs):
        job_instance = self.get_object(job)
        if not job_instance:
            return Response({'res': 'Object with job id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobSerializer(job_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, job, *args, **kwargs):
        job_instance = self.get_object(job)
        if not job_instance:
            return Response({'res': 'Object with job id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        data = {'job_name': request.data.get('job_name')}
        serializer = JobSerializer(instance=job_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job, *args, **kwargs):
        job_instance = self.get_object(job)
        if not job_instance:
            return Response({"res": "Object with job id does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        job_instance.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)


class BuildListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = BuildSerializer

    def post(self, request, *args, **kwargs):
        data = {'job': request.data.get('job'),
                'build_number': request.data.get('build_number'),
                'build_timestamp': request.data.get('build_timestamp')}
        serializer = BuildSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Build.objects.all()
        job = self.request.query_params.get('job')
        build_number = self.request.query_params.get('build_number')

        if job is not None:
            queryset = queryset.filter(job=job)
        if build_number is not None:
            queryset = queryset.filter(build_number=build_number)
        return queryset


class BuildDetailApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object_by_id(self, build_id):
        try:
            return Build.objects.get(id=build_id)
        except Build.DoesNotExist:
            return None

    def get(self, request, build_id, *args, **kwargs):
        build_instance = self.get_object_by_id(build_id)
        if not build_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BuildSerializer(build_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, build_id, *args, **kwargs):
        build_instance = self.get_object_by_id(build_id)
        if not build_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        data = {'job': request.data.get('job'),
                'build_number': request.data.get('build_number'),
                'build_timestamp': request.data.get('build_timestamp')}
        serializer = BuildSerializer(instance=build_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, build_id, *args, **kwargs):
        build_instance = self.get_object_by_id(build_id)
        if not build_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        build_instance.delete()
        return Response({'res': 'Object deleted!'}, status=status.HTTP_200_OK)


class JobResultListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobResultsSerializer

    def post(self, request, *args, **kwargs):
        data = {'job': request.data.get('job_name'),
                'build': request.data.get('build'),
                'build_url': request.data.get('build_url'),
                'build_result': request.data.get('build_result'),
                'build_git_sha': request.data.get('build_git_sha')}
        serializer = JobResultsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = JobResults.objects.all()
        job = self.request.query_params.get('job_name')
        build_number = self.request.query_params.get('build_number')
        build_result = self.request.query_params.get('build_result')

        if job is not None:
            queryset = queryset.filter(job_name=job)
        if build_number is not None:
            queryset = queryset.filter(build_number=build_number)
        if build_result is not None:
            queryset = queryset.filter(job_result=build_result)
        return queryset.order_by('-build_number')


class JobResultDetailApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, job_result):
        try:
            if isinstance(job_result, int):
                return JobResults.objects.get(id=job_result)
            elif isinstance(job_result, str):
                return JobResults.objects.get(pipeline_name=job_result)
        except Job.DoesNotExist:
            return None

    def get(self, request, job_result, *args, **kwargs):
        job_result_instance = self.get_object(job_result)
        if not job_result_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobResultsSerializer(job_result_instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, job_result, *args, **kwargs):
        job_result_instance = self.get_object(job_result)
        if not job_result_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        data = {'job': request.data.get('job_name'),
                'build': request.data.get('build'),
                'build_url': request.data.get('build_url'),
                'build_result': request.data.get('build_result'),
                'build_git_sha': request.data.get('build_git_sha')}
        serializer = JobResultsSerializer(instance=job_result_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job_result, *args, **kwargs):
        job_result_instance = self.get_object(job_result)
        if not job_result_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        job_result_instance.delete()
        return Response({'res': 'Object deleted!'}, status=status.HTTP_200_OK)
