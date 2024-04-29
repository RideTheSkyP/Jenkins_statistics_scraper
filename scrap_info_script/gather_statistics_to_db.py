import ast
import json
import time
import logging
import requests
import argparse
import datetime
from enum import Enum
from bs4 import BeautifulSoup

import constants

# Disable urllib3 warnings and debug messages
requests.packages.urllib3.disable_warnings()
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('urllib3').propagate = True

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--log_file', action='store_true', help='Option to save logs to file.')

args = parser.parse_args()

formatter = logging.Formatter('[%(levelname)s] %(message)s')
log = logging.getLogger()
fh = logging.FileHandler('scrap_info.log', 'w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

log.addHandler(fh)
log.addHandler(ch)

jobs_dict = {}
errors_dict = {}


class Result(Enum):
    SUCCESS = 0
    FAILURE = 1
    UNSTABLE = 2
    ABORTED = 3
    UNKNOWN = 3
    NOT_EXECUTED = 3


def scrap_jenkins_info(url):
    try:
        response = requests.get(f'{url}/api/python')
        response.raise_for_status()
        if response.ok:
            jenkins_info = ast.literal_eval(response.text)
            return jenkins_info
    except Exception as e:
        log.error(f'Exception occurred: {e}.')


def insert_to_db_by_api(url, data):
    retries = 0
    success = False

    while not success:
        try:
            response = requests.post(url, json=data)
            print(f'Inserted data: {data} to url: {url}')
            if not response.ok:
                raise Exception(response.text)
            success = True
        except Exception as e:
            retries += 1
            if retries > 2:
                log.error('No response after 3 retries.')
                break
            log.error(f'Exception occurred in insert to db. Error: {e}. Retrying in 10 seconds.')
            time.sleep(10)
    return response


def get_pipeline_id_from_db(pipeline_name):
    site_pipelines_rest_api = f'{constants.site_pipelines_rest_api}?pipeline_name={pipeline_name}&format=json'
    response = requests.get(site_pipelines_rest_api)
    pipeline_info = json.loads(response.text)
    pipeline_id = pipeline_info[0].get('id') if response.ok and pipeline_info else None
    return pipeline_id


def get_job_id_from_db(pipeline_id, job_name):
    site_jobs_rest_api = f'{constants.site_jobs_rest_api}?pipeline_id={pipeline_id}&job_name={job_name}&format=json'
    response = requests.get(site_jobs_rest_api)
    job_info = json.loads(response.text)
    job_id = job_info[0].get('id') if response.ok and job_info else None
    return job_id


def get_build_id_from_db(job_id, build_number):
    site_builds_rest_api = f'{constants.site_builds_rest_api}?job_id={job_id}&build_number={build_number}&format=json'
    response = requests.get(site_builds_rest_api)
    build_info = json.loads(response.text)
    build_id = build_info[0].get('id') if response.ok and build_info else None
    return build_id


def get_job_result_id_from_db(pipeline_id, job_id, build_id):
    site_job_results_rest_api = f'{constants.site_job_results_rest_api}?pipeline_id={pipeline_id}&job_id={job_id}&build_id={build_id}&format=json'
    response = requests.get(site_job_results_rest_api)
    job_result_info = json.loads(response.text)
    job_result_id = job_result_info[0].get('id') if response.ok and job_result_info else None
    return job_result_id


def get_job_failure_ids_from_db(pipeline_id, job_id, build_id):
    site_job_failure_rest_api = f'{constants.site_job_failures_rest_api}?pipeline_id={pipeline_id}&job_id={job_id}&build_id={build_id}&format=json'
    response = requests.get(site_job_failure_rest_api)
    job_failure_info = json.loads(response.text)
    job_failure_ids = [job.get('id') for job in job_failure_info if response.ok and job_failure_info]
    return job_failure_ids


def insert_into_pipelines_table(pipeline_name):
    pipeline_id = get_pipeline_id_from_db(pipeline_name)
    if not pipeline_id:
        data = {'pipeline_name': pipeline_name}
        response = insert_to_db_by_api(constants.site_pipelines_rest_api, data)
        if not response.ok:
            raise Exception(f'Couldn\'t insert data: {data} to pipelines table. '
                            f'Response: {response}, {response.content}.')
        pipeline_id = json.loads(response.text)['id']
        log.info(f'New pipeline detected, created entry for: {pipeline_name}.')
    return pipeline_id


def insert_into_jobs_table(pipeline_id, job_name):
    job_id = get_job_id_from_db(pipeline_id, job_name)
    if not job_id:
        data = {'pipeline_id': pipeline_id, 'job_name': job_name}
        response = insert_to_db_by_api(constants.site_jobs_rest_api, data)
        if not response.ok:
            raise Exception(f'Couldn\'t insert data: {data} to jobs table. '
                            f'Response: {response}, {response.content}.')
        job_id = json.loads(response.text)['id']
        log.info(f'New job detected, created entry for: {job_name}.')
    return job_id


def insert_into_builds_table(job_id, build_number, build_timestamp):
    build_id = get_build_id_from_db(job_id, build_number)
    if not build_id:
        data = {'job_id': job_id,
                'build_number': build_number,
                'build_timestamp': datetime.datetime.fromtimestamp(build_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')}
        response = insert_to_db_by_api(constants.site_builds_rest_api, data)
        if not response.ok:
            raise Exception(f'Couldn\'t insert data: {data} to build table. '
                            f'Response: {response}, {response.content}.')
        build_id = json.loads(response.text)['id']
        log.info(f'New build_number detected, created entry for: {job_id}: {build_number}.')
    return build_id


def insert_into_job_results_table(pipeline_id, job_id, build_id, build_url, build_result, build_git_sha):
    job_result_id = get_job_result_id_from_db(pipeline_id, job_id, build_id)

    if not job_result_id:
        data = {'pipeline_id': pipeline_id,
                'job_id': job_id,
                'build_id': build_id,
                'build_url': build_url,
                'build_result': Result[build_result].value,
                'build_git_sha': build_git_sha}
        response = insert_to_db_by_api(constants.site_job_results_rest_api, data)
        if not response.ok:
            raise Exception(f'Couldn\'t insert data: {data} to job_results table. '
                            f'Response: {response}, {response.content}.')
        job_result_id = json.loads(response.text)['id']
        log.info(f'New job_result entry detected, created entry for: {data}.')
    return job_result_id


def insert_into_job_failures_table(pipeline_id, job_id, build_id, job_result_id, error_type,
                                   error_file, error_message, failures_amount):
    job_failures_ids = get_job_failure_ids_from_db(pipeline_id, job_id, build_id)
    if len(job_failures_ids) <= failures_amount:
        data = {'pipeline_id': pipeline_id,
                'job_id': job_id,
                'build_id': build_id,
                'job_result_id': job_result_id,
                'error_type': error_type,
                'error_file': error_file,
                'error_message': error_message}
        response = insert_to_db_by_api(constants.site_job_failures_rest_api, data)
        if not response.ok:
            raise Exception(f'Couldn\'t insert data: {data} to job_failures table. '
                            f'Response: {response}, {response.content}.')
        job_failures_ids = json.loads(response.text)['id']
        log.info(f'New job_failure entry detected, created entry for: {data}.')
    return job_failures_ids


def add_to_dict(pipeline_name, job_name, job_number, build_url, result, build_timestamp, build_git_sha, log_link,
                job_number_internal):
    if pipeline_name not in jobs_dict:
        jobs_dict[pipeline_name] = {}
    if job_name not in jobs_dict.get(pipeline_name):
        jobs_dict[pipeline_name][job_name] = []
    jobs_dict[pipeline_name][job_name].append({'build_number': job_number,
                                               'build_url': build_url,
                                               'build_result': result,
                                               'build_timestamp': build_timestamp,
                                               'build_git_sha': build_git_sha,
                                               'log_link': log_link,
                                               'job_number_internal': job_number_internal})


def get_jobs_info_into_dict(jobs):
    for job in jobs:
        job_info = scrap_jenkins_info(job['url'])
        pipeline_name = job_info['name']
        job_name = job_info['name']
        job_builds = job_info['builds']
        for build in job_builds:
            result = None
            build_git_sha = None
            build_info = scrap_jenkins_info(build['url'])
            for action in build_info['actions']:
                result = build_info['result']
                job_number = build_info['number']
                if 'buildsByBranchName' in action:
                    build_git_sha = action['buildsByBranchName']['refs/remotes/origin/main']['marked']['SHA1']
            # Detect pipeline
            if build_info.get('_class').endswith('.WorkflowRun'):
                pipeline_url = f'{build["url"]}/wfapi'
                resp = requests.get(pipeline_url).text
                print(resp)
                stages = json.loads(resp)['stages']
                if not stages:
                    add_to_dict(pipeline_name, job_name, job_number, build_info['url'], result,
                                build_info['timestamp'], build_git_sha, None, None)
                for stage in stages:
                    link = stage['_links']['self']['href']
                    r = json.loads(requests.get(f'{constants.jenkins_base_url}/{link}').text)
                    stage_flow_nodes = r['stageFlowNodes']
                    for node in stage_flow_nodes:
                        log_link = f'{constants.jenkins_base_url}/{node["_links"]["log"]["href"]}'
                        req = json.loads(requests.get(log_link).text)
                        parsed_html = BeautifulSoup(req['text'], 'html.parser')
                        text = parsed_html.text
                        text_list = text.split('completed:')
                        if len(text_list) > 1:
                            build, completed = text_list[0], text_list[1]
                            build_str = build.split('Build')[1].strip()
                            job_name, job_number_internal = build_str.split()
                            job_name = job_name.strip()
                            result = completed.strip()
                            job_number_internal = job_number_internal.split('#')[1].strip()

                            if pipeline_name not in jobs_dict:
                                jobs_dict[pipeline_name] = {}
                            if job_name not in jobs_dict.get(pipeline_name):
                                jobs_dict[pipeline_name][job_name] = []
                            add_to_dict(pipeline_name, job_name, job_number, build_info['url'], result,
                                        build_info['timestamp'], build_git_sha, log_link, job_number_internal)
            else:
                add_to_dict(pipeline_name, job_name, job_number, build_info['url'], result, build_info['timestamp'],
                            build_git_sha, None, None)


def gather_pipelines_info():
    jobs = scrap_jenkins_info(constants.jenkins_base_url)['jobs']
    get_jobs_info_into_dict(jobs)

    for pipeline_name in jobs_dict:
        pipeline_id = insert_into_pipelines_table(pipeline_name)
        for job in jobs_dict.get(pipeline_name):
            job_id = insert_into_jobs_table(pipeline_id, job)
            for index, build in enumerate(jobs_dict.get(pipeline_name).get(job)):
                build_id = insert_into_builds_table(job_id,
                                                    build['build_number'],
                                                    build['build_timestamp'])
                job_result_id = insert_into_job_results_table(pipeline_id, job_id, build_id,
                                                              build['build_url'],
                                                              build['build_result'],
                                                              build['build_git_sha'])
                jobs_dict[pipeline_name][job][index]['pipeline_id'] = pipeline_id
                jobs_dict[pipeline_name][job][index]['job_id'] = job_id
                jobs_dict[pipeline_name][job][index]['build_id'] = build_id
                jobs_dict[pipeline_name][job][index]['job_result_id'] = job_result_id


def store_to_errors_dict(pipeline_name, job_name, build_result, job_number, error_type, error_file,
                         error_message, pipeline_id, job_id, build_id, job_result_id, failures_counter):
    if pipeline_name not in errors_dict:
        errors_dict[pipeline_name] = {}
    if job_name not in errors_dict.get(pipeline_name):
        errors_dict[pipeline_name][job_name] = []
    errors_dict[pipeline_name][job_name].append({'pipeline_id': pipeline_id,
                                                 'job_id': job_id,
                                                 'build_id': build_id,
                                                 'job_result_id': job_result_id,
                                                 'pipeline_name': pipeline_name,
                                                 'job_name': job_name,
                                                 'build_result': build_result,
                                                 'job_number': job_number,
                                                 'error_type': error_type,
                                                 'error_file': error_file,
                                                 'error_message': error_message,
                                                 'failures_counter': failures_counter})


def get_failed_job_logs_to_dict():
    for pipeline in jobs_dict:
        for job in jobs_dict.get(pipeline):
            for index, build in enumerate(jobs_dict.get(pipeline).get(job)):
                if build.get('build_result') != 'SUCCESS':
                    failures_counter = 1
                    pipeline_id = build.get('pipeline_id')
                    job_id = build.get('job_id')
                    build_id = build.get('build_id')
                    job_result_id = build.get('job_result_id')
                    job_number = build.get('job_number_internal') if build.get('job_number_internal') else build.get('build_number')
                    link = f'{constants.jenkins_base_url}/job/{pipeline}/{job_number}/consoleText'
                    text = requests.get(link).text
                    if 'AssertionError' in text:
                        error_text = text.split('+')[-1].split('\n')
                        error_file = error_text[0].split('python3')[1].strip()
                        error_message = [t for t in error_text if 'assert' in t][0].strip()
                        error_type = 'AssertionError'
                        store_to_errors_dict(pipeline, job, build.get('build_result'), job_number,
                                             error_type, error_file, error_message, pipeline_id, job_id, build_id,
                                             job_result_id, failures_counter)
                    elif 'WorkflowScript' in text:
                        failures_counter = text.count('WorkflowScript')
                        error_text = text.split('startup failed:')[-1].split('\n')
                        error_file = None
                        error_type = 'WorkflowScript'
                        for index, t in enumerate(error_text):
                            if 'WorkflowScript' in t:
                                error_message = '\n'.join(error_text[index:index + 2])
                                store_to_errors_dict(pipeline, job, build.get('build_result'), job_number,
                                                     error_type, error_file, error_message, pipeline_id, job_id,
                                                     build_id, job_result_id, failures_counter)
                    elif 'GitException' in text:
                        error_file = None
                        error_type = 'GitException'
                        error_message = [t for t in text.split('\n') if 'fatal' in t][0].strip()
                        store_to_errors_dict(pipeline, job, build.get('build_result'), job_number,
                                             error_type, error_file, error_message, pipeline_id, job_id, build_id,
                                             job_result_id, failures_counter)
                    else:
                        print('ELSE NOT CAUGHT ERROR', text)


def gather_job_logs():
    get_failed_job_logs_to_dict()

    for pipeline_name in errors_dict:
        for job in errors_dict.get(pipeline_name):
            for index, build in enumerate(errors_dict.get(pipeline_name).get(job)):
                job_failure_id = insert_into_job_failures_table(build.get('pipeline_id'),
                                                                build.get('job_id'),
                                                                build.get('build_id'),
                                                                build.get('job_result_id'),
                                                                build.get('error_type'),
                                                                build.get('error_file'),
                                                                build.get('error_message'),
                                                                build.get('failures_counter'))


def main():
    gather_pipelines_info()
    gather_job_logs()
    # print(json.dumps(errors_dict, indent=4))


if __name__ == '__main__':
    main()
