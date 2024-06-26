from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView

from jenkins_statistics.models import Pipeline, Job, Build, JobResults, JobFailures
from .serializers import PipelineSerializer, JobSerializer, BuildSerializer, JobResultsSerializer, JobFailuresSerializer


class PipelineListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = PipelineSerializer

    def post(self, request, *args, **kwargs):
        data = {'pipeline_name': request.data.get('pipeline_name')}
        serializer = PipelineSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Pipeline.objects.all()
        pipeline_id = self.request.query_params.get('id')
        pipeline_name = self.request.query_params.get('pipeline_name')
        if pipeline_id is not None:
            queryset = queryset.filter(id=pipeline_id)
        if pipeline_name is not None:
            queryset = queryset.filter(pipeline_name=pipeline_name)
        return queryset


class PipelineDetailApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, pipeline):
        try:
            if isinstance(pipeline, int):
                return Pipeline.objects.get(id=pipeline)
            elif isinstance(pipeline, str):
                return Pipeline.objects.get(pipeline_name=pipeline)
        except Pipeline.DoesNotExist:
            return None

    def get(self, request, pipeline, *args, **kwargs):
        pipeline_instance = self.get_object(pipeline)
        if not pipeline_instance:
            return Response({'res': 'Object with pipeline id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PipelineSerializer(pipeline_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pipeline, *args, **kwargs):
        pipeline_instance = self.get_object(pipeline)
        if not pipeline_instance:
            return Response({'res': 'Object with pipeline id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        data = {'pipeline_name': request.data.get('pipeline_name')}
        serializer = PipelineSerializer(instance=pipeline_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pipeline, *args, **kwargs):
        pipeline_instance = self.get_object(pipeline)
        if not pipeline_instance:
            return Response({'res': 'Object with pipeline id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        pipeline_instance.delete()
        return Response({'res': 'Object deleted!'}, status=status.HTTP_200_OK)


class JobListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobSerializer

    def post(self, request, *args, **kwargs):
        data = {'pipeline': request.data.get('pipeline_id'),
                'job_name': request.data.get('job_name')}
        serializer = JobSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Job.objects.all()
        pipeline_id = self.request.query_params.get('pipeline_id')
        job_id = self.request.query_params.get('id')
        job_name = self.request.query_params.get('job_name')

        if pipeline_id is not None:
            queryset = queryset.filter(pipeline=pipeline_id)
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
        data = {'pipeline': request.data.get('pipeline_id'),
                'job_name': request.data.get('job_name')}
        serializer = JobSerializer(instance=job_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job, *args, **kwargs):
        job_instance = self.get_object(job)
        if not job_instance:
            return Response({'res': 'Object with job id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        job_instance.delete()
        return Response({'res': 'Object deleted!'}, status=status.HTTP_200_OK)


class BuildListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = BuildSerializer

    def post(self, request, *args, **kwargs):
        data = {'job': request.data.get('job_id'),
                'build_number': request.data.get('build_number'),
                'build_timestamp': request.data.get('build_timestamp')}
        serializer = BuildSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Build.objects.all()
        job_id = self.request.query_params.get('job_id')
        build_id = self.request.query_params.get('build_id')
        build_number = self.request.query_params.get('build_number')

        if job_id is not None:
            queryset = queryset.filter(job=job_id)
        if build_id is not None:
            queryset = queryset.filter(id=build_id)
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
        data = {'job': request.data.get('job_id'),
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
        data = {'pipeline': request.data.get('pipeline_id'),
                'job': request.data.get('job_id'),
                'build': request.data.get('build_id'),
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
        pipeline_id = self.request.query_params.get('pipeline_id')
        job_id = self.request.query_params.get('job_id')
        build_id = self.request.query_params.get('build_id')
        build_result = self.request.query_params.get('build_result')

        if pipeline_id is not None:
            queryset = queryset.filter(pipeline_id=pipeline_id)
        if job_id is not None:
            queryset = queryset.filter(job_id=job_id)
        if build_id is not None:
            queryset = queryset.filter(build_id=build_id)
        if build_result is not None:
            queryset = queryset.filter(job_result=build_result)
        return queryset.order_by('-build')


class JobResultDetailApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, job_result):
        try:
            if isinstance(job_result, int):
                return JobResults.objects.get(id=job_result)
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
        data = {'pipeline': request.data.get('pipeline_id'),
                'job': request.data.get('job_id'),
                'build': request.data.get('build_id'),
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


class JobFailuresListApiView(ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobFailuresSerializer

    def post(self, request, *args, **kwargs):
        data = {'pipeline': request.data.get('pipeline_id'),
                'job': request.data.get('job_id'),
                'build': request.data.get('build_id'),
                'job_result': request.data.get('job_result_id'),
                'error_type': request.data.get('error_type'),
                'error_file': request.data.get('error_file'),
                'error_message': request.data.get('error_message')}
        serializer = JobFailuresSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = JobFailures.objects.all()
        pipeline_id = self.request.query_params.get('pipeline_id')
        job_id = self.request.query_params.get('job_id')
        build_id = self.request.query_params.get('build_id')
        job_result_id = self.request.query_params.get('job_result_id')
        error_type = self.request.query_params.get('error_type')
        error_file = self.request.query_params.get('error_file')

        if pipeline_id is not None:
            queryset = queryset.filter(pipeline_id=pipeline_id)
        if job_id is not None:
            queryset = queryset.filter(job_id=job_id)
        if build_id is not None:
            queryset = queryset.filter(build_id=build_id)
        if job_result_id is not None:
            queryset = queryset.filter(job_result_id=job_result_id)
        if error_type is not None:
            queryset = queryset.filter(error_type=error_type)
        if error_file is not None:
            queryset = queryset.filter(error_file=error_file)
        return queryset


class JobFailuresDetailApiView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, job_failure_id):
        try:
            if isinstance(job_failure_id, int):
                return JobFailures.objects.get(id=job_failure_id)
        except Job.DoesNotExist:
            return None

    def get(self, request, job_failure_id, *args, **kwargs):
        job_failure_instance = self.get_object(job_failure_id)
        if not job_failure_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobFailuresSerializer(job_failure_instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, job_failure_id, *args, **kwargs):
        job_job_failure_instance = self.get_object(job_failure_id)
        if not job_job_failure_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        data = {'pipeline': request.data.get('pipeline_id'),
                'job': request.data.get('job_id'),
                'build': request.data.get('build_id'),
                'job_result': request.data.get('job_result_id'),
                'error_type': request.data.get('error_type'),
                'error_file': request.data.get('error_file'),
                'error_message': request.data.get('error_message')}
        serializer = JobFailuresSerializer(instance=job_job_failure_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job_failure_id, *args, **kwargs):
        job_job_failure_instance = self.get_object(job_failure_id)
        if not job_job_failure_instance:
            return Response({'res': 'Object with build id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        job_job_failure_instance.delete()
        return Response({'res': 'Object deleted!'}, status=status.HTTP_200_OK)
