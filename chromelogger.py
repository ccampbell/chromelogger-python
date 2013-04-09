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
import logging
import re

import jsonpickle

version = '0.2.2'

HEADER_NAME = 'X-ChromeLogger-Data'
JSON_HEADER = {
    'version': version,
    'columns': ['log', 'backtrace', 'type'],
}
PYTHON_INTERPOLATION = re.compile(r'''(
    %  # the percent character
    (?:\([0-9a-z_]+\))?  # mapping
    [#0 +-]*  # conversion flags
    [*0-9]*  # minimum width
    (?:.[*0-9]*)?  # precision
    [hlL]?  # length modifier
    [diouxXeEfFgGcrs%]  # conversion
    )''', re.X)

_last_backtrace = None
rows = []
backtrace_level = 2


def _convert(data):
    serialized = json.loads(jsonpickle.encode(data))
    if isinstance(serialized, dict):
        serialized['___class_name'] = serialized.pop('py/object')
    return serialized


def _reformat_msg(msg, args):
    unclaimed = args[:]
    tokens = PYTHON_INTERPOLATION.split(msg)
    parts = []
    for token in tokens:
        if token.startswith('%') and not token.startswith(r'%%'):
            arg = unclaimed.pop(0)
            if isinstance(arg, dict):
                parts.append('%O')
            else:
                parts.append('%s')
        else:
            parts.append(token)
    return ''.join(parts)


def _log(typ, msg, args, backtrace):
    global _last_backtrace
    if backtrace == _last_backtrace:
        backtrace = None
    else:
        _last_backtrace = backtrace
    args = [_convert(arg) for arg in args]
    msg = _reformat_msg(msg, args)
    row = [[msg] + args, backtrace, typ]
    rows.append(row)


def _encode(data):
    json_data = json.dumps(data)
    utf8_encode_data = json_data.encode('utf-8')
    return utf8_encode_data.encode('base64').replace('\n', '')


def get_header():
    global rows
    if not rows:
        return None
    res = (HEADER_NAME, _encode(dict(JSON_HEADER, rows=rows)))
    rows = []
    return res


class DjangoMiddleware(object):
    '''
    This is middleware for django

    After this module is installed just add "chromelogger.DjangoMiddleware"
    to your MIDDLEWARE_CLASSES in settings.py
    '''
    def process_response(self, request, response):
        header = get_header()
        if header is not None:
            response[header[0]] = header[1]

        return response


class ChromeHandler(logging.StreamHandler):

    def emit(self, record):
        level = 'log'
        if record.levelno >= logging.ERROR:
            level = 'error'
        elif record.levelno >= logging.WARNING:
            level = 'warn'
        elif record.levelno >= logging.INFO:
            level = 'info'
        backtrace = '%s:%d, %s()' % (record.pathname, record.lineno,
                                     record.funcName)
        _log(level, record.msg, record.args, backtrace)

    def flush(self):
        pass
