# Copyright 2013 Craig Campbell
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

# use custom name
jsonpickle.tags.OBJECT = '___class_name'
set_header = None
version = '0.2.2'


class Console(object):
    HEADER_NAME = 'X-ChromeLogger-Data'

    _instance = None

    def __init__(self):
        global version

        self.json = {
            'version': version,
            'columns': ['log', 'backtrace', 'type'],
            'rows': []
        }
        self.backtrace_level = 2
        self.backtraces = []

    @staticmethod
    def instance():
        if Console._instance is None:
            Console._instance = Console()

        return Console._instance

    def _is_literal(self, data):
        return data is None or isinstance(data, (str, int, long, float, bool))

    def _convert(self, data):
        return json.loads(jsonpickle.encode(data))

    def _log(self, args):
        type = args[0:1]
        args = args[1:]

        # since this is data being transmitted as a header setting
        # log to empty string is just a way to send less data
        # the extension defaults to doing console.log
        if type == 'log':
            type = ''

        logs = []
        for arg in args:
            logs.append(self._convert(arg))

        backtrace_info = traceback.extract_stack()[:-self.backtrace_level].pop()

        # path/to/file.py : line_number
        backtrace = backtrace_info[0] + ' : ' + str(backtrace_info[1])

        # if two logs are on the same line (for example in a loop)
        # then we should not log the backtrace again
        if backtrace in self.backtraces:
            backtrace = None

        # store backtraces in list so we can tell later if it was
        # already used
        if backtrace is not None:
            self.backtraces.append(backtrace)

        self._add_row(logs, backtrace=backtrace, type=type)

    def _add_row(self, logs, backtrace=None, type=''):
        global set_header

        row = [logs, backtrace, type]
        self.json['rows'].append(row)

        # if a set_header function is defined then we will
        # call that with each row added
        #
        # this class is a singleton so it will just overwrite
        # the existing header with more data each time
        if set_header is not None:
            set_header(Console.HEADER_NAME, self._encode(self.json))

    def _encode(self, data):
        json_data = json.dumps(data)
        utf8_encode_data = json_data.encode('utf-8')
        return utf8_encode_data.encode('base64').replace('\n', '')

    def _get_header(self):
        if len(self.json['rows']) == 0:
            return None

        return (Console.HEADER_NAME, self._encode(self.json))


def reset():
    Console._instance = None


def get_header(flush=True):
    header = Console.instance()._get_header()
    if flush:
        reset()

    return header


def log(*args):
    args = ('log',) + args
    Console.instance()._log(args)


def warn(*args):
    args = ('warn',) + args
    Console.instance()._log(args)


def error(*args):
    args = ('error',) + args
    Console.instance()._log(args)


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
