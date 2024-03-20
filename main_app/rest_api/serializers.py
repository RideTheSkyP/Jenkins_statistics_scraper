from rest_framework import serializers
from jenkins_statistics.models import Job, Build, JobResults


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['id',  'job_name']


class BuildSerializer(serializers.ModelSerializer):
    job_id = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())

    class Meta:
        model = Build
        fields = ['id', 'job_id', 'build_number', 'build_timestamp']


class JobResultsSerializer(serializers.ModelSerializer):
    job_id = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())
    build_id = serializers.SlugRelatedField(slug_field='id', queryset=Build.objects.all())

    class Meta:
        model = JobResults
        fields = ['id', 'job_id', 'build_id', 'build_url', 'build_result', 'build_git_sha']
