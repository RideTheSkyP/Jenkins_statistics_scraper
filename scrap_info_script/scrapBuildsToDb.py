import ast
import logging
import sqlite3
import requests
import argparse
import datetime

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


def parseArgumentStr(exclude_str):
    return exclude_str.split(',') if exclude_str else []


def parseArguments(argument):
    arguments = parseArgumentStr(argument)
    split_args = '|'.join(arguments)
    regex = fr'.*({split_args}).*' if split_args else r'\*'
    return regex


def scrap_jenkins_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.ok:
            jenkins_info = ast.literal_eval(response.text)
            return jenkins_info
    except Exception as e:
        log.error(f'Exception occurred: {e}.')


def main():
    scrap_jenkins_info('http://localhost:8080/api/python')


if __name__ == '__main__':
    main()
