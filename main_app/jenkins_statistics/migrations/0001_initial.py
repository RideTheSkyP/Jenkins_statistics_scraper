# Generated by Django 4.2.11 on 2024-03-19 12:40

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('build_number', models.IntegerField(default=1)),
                ('build_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobResults',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('build_url', models.CharField(max_length=100)),
                ('build_result', models.IntegerField(default=1)),
                ('build_git_sha', models.CharField(max_length=100)),
                ('build', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jenkins_statistics.build')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jenkins_statistics.job')),
            ],
        ),
        migrations.AddField(
            model_name='build',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jenkins_statistics.job'),
        ),
    ]
