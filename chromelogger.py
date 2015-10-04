# Copyright 2015 Craig Campbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# uses Chrome Logger extension for logging
# @see https://chrome.google.com/webstore/detail/noaneddfkdjfnfdakjjmocngnfkfehhd
# @see http://chromelogger.com
import json
import traceback
import jsonpickle
from base64 import b64encode

# use custom name
# @todo do not do this globally
jsonpickle.tags.OBJECT = '___class_name'

version = '0.4.2'
HEADER_NAME = 'X-ChromeLogger-Data'
BACKTRACE_LEVEL = 2
DATA = {
    'version': version,
    'columns': ['log', 'backtrace', 'type']
}

set_header = None
rows = []
backtraces = []


def _convert(data):
    return json.loads(jsonpickle.encode(data))


def _log(args):
    global backtraces

    type = args[0:1]
    args = args[1:]

    # since this is data being transmitted as a header setting
    # log to empty string is just a way to send less data
    # the extension defaults to doing console.log
    if type == 'log':
        type = ''

    logs = [_convert(arg) for arg in args]

    backtrace_info = traceback.extract_stack()[:-BACKTRACE_LEVEL].pop()

    # path/to/file.py : line_number
    backtrace = '%s : %s' % (backtrace_info[0], backtrace_info[1])

    # if two logs are on the same line (for example in a loop)
    # then we should not log the backtrace again
    if backtrace in backtraces:
        backtrace = None

    # store backtraces in list so we can tell later if it was
    # already used
    if backtrace is not None:
        backtraces.append(backtrace)

    _add_row(logs, backtrace=backtrace, type=type)


def _add_row(logs, backtrace=None, type=''):
    global rows

    row = [logs, backtrace, type]
    rows.append(row)

    # if a set_header function is defined then we will
    # call that with each row added
    #
    # this class is a singleton so it will just overwrite
    # the existing header with more data each time
    if set_header is not None:
        header = get_header(flush=False)
        set_header(header[0], header[1])


def _encode(data):
    json_data = json.dumps(data)
    utf8_encode_data = json_data.encode()
    return b64encode(utf8_encode_data)


def reset():
    global rows, backtraces
    rows = []
    backtraces = []


def get_header(flush=True):
    header = None
    if len(rows) > 0:
        header = (HEADER_NAME, _encode(dict(DATA, rows=rows)))

    if flush:
        reset()

    return header


def log(*args):
    args = ('log',) + args
    _log(args)


def warn(*args):
    args = ('warn',) + args
    _log(args)


def error(*args):
    args = ('error',) + args
    _log(args)


def info(*args):
    args = ('info',) + args
    _log(args)


def group(*args):
    args = ('group',) + args
    _log(args)


def group_end(*args):
    args = ('groupEnd',) + args
    _log(args)


def group_collapsed(*args):
    args = ('groupCollapsed',) + args
    _log(args)


def table(*args):
    args = ('table',) + args
    _log(args)


# this is middleware for django.  ater this module is installed just add
# "chromelogger.DjangoMiddleware" to your MIDDLEWARE_CLASSES in settings.py
#
# after that you can just
# import chromelogger
# chromelogger.log('Hello world!')
#
# from anywhere in your Django application
class DjangoMiddleware(object):
    def process_response(self, request, response):
        header = get_header()
        if header is not None:
            response[header[0]] = header[1]

        return response
