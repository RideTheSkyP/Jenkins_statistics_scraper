import json
from django.shortcuts import render

from .models import Pipeline, Job, Build, JobResults


def index(request):
    job_results_dict = {}
    id_to_pipeline_dict = {}
    id_to_job_dict = {}
    id_to_build_dict = {}
    build_numbers_by_pipelines = {}
    job_results_queryset = JobResults.objects.values()

    for job_result in job_results_queryset:
        if not id_to_pipeline_dict.get(job_result['pipeline_id']):
            pipeline = Pipeline.objects.get(id=job_result['pipeline_id'])
            id_to_pipeline_dict[job_result['pipeline_id']] = pipeline
        if not id_to_job_dict.get(job_result['job_id']):
            job = Job.objects.get(id=job_result['job_id'])
            id_to_job_dict[job_result['job_id']] = job
        if not id_to_build_dict.get(job_result['build_id']):
            build = Build.objects.get(id=job_result['build_id'])
            id_to_build_dict[job_result['build_id']] = build
        pipeline = id_to_pipeline_dict.get(job_result['pipeline_id'])
        job = id_to_job_dict.get(job_result['job_id'])
        build = id_to_build_dict.get(job_result['build_id'])
        if not job_results_dict.get(pipeline.pipeline_name):
            job_results_dict[pipeline.pipeline_name] = {}
            build_numbers_by_pipelines[pipeline.pipeline_name] = []
        if not job_results_dict.get(pipeline.pipeline_name).get(job.job_name):
            job_results_dict[pipeline.pipeline_name][job.job_name] = []
        job_results_dict[pipeline.pipeline_name][job.job_name].append({'pipeline_name': pipeline.pipeline_name,
                                                                       'job_name': job.job_name,
                                                                       'build_number': build.build_number,
                                                                       'build_url': job_result['build_url'],
                                                                       'build_result': job_result['build_result'],
                                                                       'build_git_sha': job_result['build_git_sha']})
        build_numbers_by_pipelines[pipeline.pipeline_name].append(build.build_number)
    for pipeline_name in job_results_dict:
        for job_name in job_results_dict.get(pipeline_name):
            values = job_results_dict.get(pipeline_name).get(job_name)
            job_results_dict[pipeline_name][job_name] = sorted(values, key=lambda item: item['build_number'])
    context = {
        'job_results_dict': json.dumps(job_results_dict),
        'build_numbers': json.dumps(build_numbers_by_pipelines)
    }
    return render(request, 'index.html', context)


def test_results(request):
    return render(request, 'test_results.html', {})


def test_failures(request):
    return render(request, 'test_failures.html', {})
