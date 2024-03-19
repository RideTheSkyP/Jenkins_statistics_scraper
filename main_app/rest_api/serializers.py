from rest_framework import serializers
from jenkins_statistics.models import Job, Build, JobResults


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['id',  'job_name']


class BuildSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())

    class Meta:
        model = Build
        fields = ['id', 'job', 'build_number', 'build_timestamp']


class JobResultsSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())
    build = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())

    class Meta:
        model = JobResults
        fields = ['id', 'job', 'build', 'build_url', 'build_result', 'build_git_sha']
