from rest_framework import serializers
from jenkins_statistics.models import Pipeline, Job, Build, JobResults


class PipelineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pipeline
        fields = ['id',  'pipeline_name']


class JobSerializer(serializers.ModelSerializer):
    pipeline = serializers.SlugRelatedField(slug_field='id', queryset=Pipeline.objects.all())

    class Meta:
        model = Job
        fields = ['id', 'pipeline', 'job_name']


class BuildSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())

    class Meta:
        model = Build
        fields = ['id', 'job', 'build_number', 'build_timestamp']


class JobResultsSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(slug_field='id', queryset=Job.objects.all())
    build = serializers.SlugRelatedField(slug_field='id', queryset=Build.objects.all())
    pipeline = serializers.SlugRelatedField(slug_field='id', queryset=Pipeline.objects.all())

    class Meta:
        model = JobResults
        fields = ['id', 'pipeline', 'job', 'build', 'build_url', 'build_result', 'build_git_sha']
