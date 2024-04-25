from enum import Enum
from datetime import datetime
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def trim_last_number_from_url(dictionary, url):
    return ''.join(url.rsplit('/', 2)[0])


class Result(Enum):
    SUCCESS = 0
    FAILURE = 1
    ABORTED = 2
    UNKNOWN = 2


@register.filter
def convert_result_from_num_to_literal(dictionary, result):
    return Result(result).name


@register.filter
def convert_literal_date_to_timestamp(dictionary, date):
    return int(datetime.timestamp(date))
