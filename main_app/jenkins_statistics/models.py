import django.utils
from django.db import models


class Job(models.Model):
    job_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.job_name


class Build(models.Model):
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    build_number = models.IntegerField(default=1)
    build_timestamp = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        unique_together = ('job_id', 'build_number')


class JobResults(models.Model):
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    build_id = models.ForeignKey(Build, on_delete=models.CASCADE)
    build_url = models.CharField(max_length=100)
    build_result = models.IntegerField(default=1)
    build_git_sha = models.CharField(max_length=100)

    class Meta:
        unique_together = ('job_id', 'build_id')
