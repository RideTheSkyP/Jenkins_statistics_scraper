import django.utils
from django.db import models


class Pipeline(models.Model):
    pipeline_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.pipeline_name


class Job(models.Model):
    job_name = models.CharField(max_length=100)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('job_name', 'pipeline')

    def __str__(self):
        return self.job_name


class Build(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    build_number = models.IntegerField(default=1)
    build_timestamp = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        unique_together = ('job', 'build_number')

    def __str__(self):
        return str(self.build_number)


class JobResults(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    build_url = models.CharField(max_length=100)
    build_result = models.IntegerField(default=1)
    build_git_sha = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ('pipeline', 'job', 'build')

    def __str__(self):
        return str(self.build_result)


class JobFailures(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    build = models.ForeignKey(Build, on_delete=models.CASCADE)
    job_result = models.ForeignKey(JobResults, on_delete=models.CASCADE)
    error_type = models.CharField(max_length=100)
    error_file = models.CharField(max_length=100, null=True)
    error_message = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.error_type)
