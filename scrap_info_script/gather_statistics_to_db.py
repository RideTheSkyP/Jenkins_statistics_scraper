import ast
import json
import time
import logging
import sqlite3
import requests
import argparse
import datetime
from enum import Enum

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


class Result(Enum):
    SUCCESS = 0
    FAILURE = 1
    ABORTED = 2
    UNKNOWN = 2


def parseArgumentStr(exclude_str):
    return exclude_str.split(',') if exclude_str else []


def parseArguments(argument):
    arguments = parseArgumentStr(argument)
    split_args = '|'.join(arguments)
    regex = fr'.*({split_args}).*' if split_args else r'\*'
    return regex


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
            response = requests.post(url, json=data, verify=False)
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


def get_job_id_from_db(job_name):
    site_jobs_rest_api = f'{constants.site_jobs_rest_api}?job_name={job_name}&format=json'
    response = requests.get(site_jobs_rest_api, verify=False)
    job_info = json.loads(response.text)
    job_id = job_info[0].get('id') if response.ok and job_info else None
    return job_id


def get_build_id_from_db(job_id, build_number):
    site_builds_rest_api = f'{constants.site_builds_rest_api}?job_id={job_id}&build_number={build_number}&format=json'
    response = requests.get(site_builds_rest_api, verify=False)
    build_info = json.loads(response.text)
    build_id = build_info[0].get('id') if response.ok and build_info else None
    return build_id


def get_job_result_id_from_db(job_id, build_id):
    site_job_results_rest_api = f'{constants.site_job_results_rest_api}?job_id={job_id}&build_id={build_id}&format=json'
    response = requests.get(site_job_results_rest_api, verify=False)
    job_result_info = json.loads(response.text)
    job_result_id = job_result_info[0].get('id') if response.ok and job_result_info else None
    return job_result_id


def insert_into_jobs_table(job_name):
    job_id = get_job_id_from_db(job_name)
    if not job_id:
        data = {'job_name': job_name}
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
                'build_timestamp': datetime.datetime.fromtimestamp(build_timestamp/1000).strftime("%Y-%m-%d %H:%M:%S")}
        response = insert_to_db_by_api(constants.site_builds_rest_api, data)
        if not response.ok:
            raise Exception(f'Couldn\'t insert data: {data} to build table. '
                            f'Response: {response}, {response.content}.')
        build_id = json.loads(response.text)['id']
        log.info(f'New build_number detected, created entry for: {job_id}: {build_number}.')
    return build_id


def insert_into_job_results_table(job_id, build_id, build_url, build_result, build_git_sha):
    job_result_id = get_job_result_id_from_db(job_id, build_id)

    if not job_result_id:
        data = {'job_id': job_id,
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


def get_jobs_info_into_dict(jobs):
    jobs_dict = {}
    for job in jobs:
        job_info = scrap_jenkins_info(job['url'])
        job_name = job_info['name']
        job_builds = job_info['builds']
        if job_name not in jobs_dict:
            jobs_dict[job_name] = []
        for build in job_builds:
            build_git_sha = None
            build_info = scrap_jenkins_info(build['url'])
            for action in build_info['actions']:
                if 'buildsByBranchName' in action:
                    build_git_sha = action['buildsByBranchName']['refs/remotes/origin/main']['marked']['SHA1']
            jobs_dict[job_name].append({'build_number': build_info['number'],
                                        'build_url': build_info['url'],
                                        'build_result': build_info['result'],
                                        'build_timestamp': build_info['timestamp'],
                                        'build_git_sha': build_git_sha})
    return jobs_dict


def main():
    jobs = scrap_jenkins_info(constants.jenkins_base_url)['jobs']
    jobs_dict = get_jobs_info_into_dict(jobs)
    for job in jobs_dict:
        job_id = insert_into_jobs_table(job)
        for build in jobs_dict[job]:
            build_id = insert_into_builds_table(job_id, build['build_number'], build['build_timestamp'])
            job_result_id = insert_into_job_results_table(job_id, build_id, build['build_url'], build['build_result'], build['build_git_sha'])


if __name__ == '__main__':
    main()
