# uses Chrome Logger extension for logging
# https://chrome.google.com/webstore/detail/noaneddfkdjfnfdakjjmocngnfkfehhd
import json
import traceback
import jsonpickle

# use custom name
jsonpickle.tags.OBJECT = '___class_name'
set_header = None


class Console(object):
    VERSION = '0.2.1'
    HEADER_NAME = 'X-ChromeLogger-Data'

    _instance = None

    def __init__(self):
        self.json = {
            'version': Console.VERSION,
            'columns': ['log', 'backtrace', 'type'],
            'rows': []
        }
        self.backtrace_level = 2
        self.backtraces = []
        self.objects = []

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

        if type == 'log':
            type = ''

        logs = []
        for arg in args:
            logs.append(self._convert(arg))

        backtrace_info = traceback.extract_stack()[:-self.backtrace_level].pop()

        backtrace = backtrace_info[0] + ' : ' + str(backtrace_info[1])

        if backtrace in self.backtraces:
            backtrace = None

        if backtrace is not None:
            self.backtraces.append(backtrace)

        self._add_row(logs, backtrace=backtrace, type=type)

    def _add_row(self, logs, backtrace=None, type=''):
        global set_header

        row = [logs, backtrace, type]
        self.json['rows'].append(row)

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


def get_header(flush=True):
    header = Console.instance()._get_header()
    if flush:
        reset()

    return header


def reset():
    Console._instance = None


def log(*args):
    args = ('log',) + args
    Console.instance()._log(args)


def warn(*args):
    args = ('warn',) + args
    Console.instance()._log(args)


def error(*args):
    args = ('error',) + args
    Console.instance()._log(args)


class DjangoMiddleware(object):
    def process_response(self, request, response):
        header = get_header()
        if header is not None:
            response[header[0]] = header[1]

        return response
