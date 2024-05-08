import json
import pandas as pd
from django.shortcuts import render

from .models import Pipeline, Job, Build, JobResults, JobFailures

id_to_job_dict = {}
id_to_build_dict = {}
id_to_pipeline_dict = {}
id_to_job_result_dict = {}
build_numbers_by_pipelines = {}


def index(request):
    job_results_dict = {}
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
        pipeline_build_numbers = build_numbers_by_pipelines[pipeline_name]
        build_numbers_by_pipelines[pipeline_name] = sorted(list(set(pipeline_build_numbers)), reverse=True)
        job_names = job_results_dict.get(pipeline_name)
        job_names_order = ['check_files', 'aaaa', 'check_requirements', 'run_tests', 'scrap_data_to_db']
        ordered_job_names = {}

        if len(job_names.keys()) > 1:
            for jn in job_names_order:
                ordered_job_names[jn] = job_names[jn]
        else:
            ordered_job_names = job_names

        for job_name, values in ordered_job_names.items():
            job_results_dict[pipeline_name][job_name] = sorted(values, key=lambda item: item['build_number'])
    context = {
        'job_results_dict': json.dumps(job_results_dict),
        'build_numbers': json.dumps(build_numbers_by_pipelines)
    }
    return render(request, 'index.html', context)


def test_results(request):
    job_failures_dict = []
    job_results_with_foreign_keys_joined = JobResults.objects.select_related('pipeline') \
        .select_related('job').select_related('build').all()

    for jr in job_results_with_foreign_keys_joined:
        job_failures_dict.append({'pipeline_name': jr.pipeline.pipeline_name,
                                  'build_timestamp': jr.build.build_timestamp.strftime('%m/%d/%Y'),
                                  'build_result': jr.build_result
                                  })
    df = pd.DataFrame(job_failures_dict)
    group_df = df.groupby(['pipeline_name', 'build_timestamp'])
    result_counts = group_df['build_result'].apply(lambda x: (x == 0).sum())
    total_counts = group_df['build_result'].count()
    percentage = round((result_counts / total_counts) * 100, 2)
    result_df = pd.DataFrame({'percentage': percentage}).reset_index()
    df = pd.merge(group_df.size().reset_index(), result_df, on=['pipeline_name', 'build_timestamp'], how='left')
    df.columns = ['pipeline_name', 'build_timestamp', 'total_builds', 'percentage']
    df_to_dict = df.to_dict('records')
    result_dict = {}
    for record in df_to_dict:
        if not result_dict.get(record.get('pipeline_name')):
            result_dict[record.get('pipeline_name')] = {'build_timestamp': [],
                                                        'total_builds': [],
                                                        'percentage': []}
        result_dict[record.get('pipeline_name')]['build_timestamp'].append(record['build_timestamp'])
        result_dict[record.get('pipeline_name')]['total_builds'].append(record['total_builds'])
        result_dict[record.get('pipeline_name')]['percentage'].append(record['percentage'])
    return render(request, 'test_results.html', {'df': json.dumps(result_dict)})


def test_failures(request):
    job_failures_dict = {}
    job_failures_queryset = JobFailures.objects.values()

    for job_failure in job_failures_queryset:
        if not id_to_pipeline_dict.get(job_failure['pipeline_id']):
            pipeline = Pipeline.objects.get(id=job_failure['pipeline_id'])
            id_to_pipeline_dict[job_failure['pipeline_id']] = pipeline
        if not id_to_job_dict.get(job_failure['job_id']):
            job = Job.objects.get(id=job_failure['job_id'])
            id_to_job_dict[job_failure['job_id']] = job
        if not id_to_build_dict.get(job_failure['build_id']):
            build = Build.objects.get(id=job_failure['build_id'])
            id_to_build_dict[job_failure['build_id']] = build
        if not id_to_job_result_dict.get(job_failure['job_result_id']):
            job_result = JobResults.objects.get(id=job_failure['job_result_id'])
            id_to_job_result_dict[job_failure['job_result_id']] = job_result

        pipeline = id_to_pipeline_dict.get(job_failure.get('pipeline_id'))
        job = id_to_job_dict.get(job_failure.get('job_id'))
        build = id_to_build_dict.get(job_failure.get('build_id'))
        job_result = id_to_job_result_dict.get(job_failure.get('job_result_id'))
        if not job_failures_dict.get(pipeline.pipeline_name):
            job_failures_dict[pipeline.pipeline_name] = {}
        if not job_failures_dict.get(pipeline.pipeline_name).get(job.job_name):
            job_failures_dict[pipeline.pipeline_name][job.job_name] = []
        job_failures_dict[pipeline.pipeline_name][job.job_name].append({'pipeline_name': pipeline.pipeline_name,
                                                                        'job_name': job.job_name,
                                                                        'build_number': build.build_number,
                                                                        'build_result': job_result.build_result,
                                                                        'build_timestamp': build.build_timestamp,
                                                                        'build_url': job_result.build_url,
                                                                        'error_type': job_failure.get('error_type'),
                                                                        'error_file': job_failure.get('error_file'),
                                                                        'error_message': job_failure.get('error_message')})
    return render(request, 'test_failures.html', {'job_failures_dict': job_failures_dict})
