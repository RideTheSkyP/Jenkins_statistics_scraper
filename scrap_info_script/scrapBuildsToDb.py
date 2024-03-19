import ast
import logging
import sqlite3
import requests
import argparse
import datetime
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


def get_jobs_info_into_dict(jobs):
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


def main():
    jobs = scrap_jenkins_info(constants.jenkins_base_url)['jobs']
    get_jobs_info_into_dict(jobs)
    print(jobs_dict)


if __name__ == '__main__':
    main()
