import os
import sys
import yaml
import string
import logging
import pkgutil
from importlib import import_module
from argparse import HelpFormatter
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from docutils.core import publish_string
from docutils.writers.html4css1 import Writer, HTMLTranslator

POSIX = os.name != 'nt'

# colourful logging
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, _NOTHING, DEFAULT = range(10)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
COLOR_PATTERN = "%s%s%%s%s" % (COLOR_SEQ, COLOR_SEQ, RESET_SEQ)
LEVEL_COLOR_MAPPING = {
    logging.DEBUG: (BLUE, DEFAULT),
    logging.INFO: (GREEN, DEFAULT),
    logging.WARNING: (YELLOW, DEFAULT),
    logging.ERROR: (RED, DEFAULT),
    logging.CRITICAL: (WHITE, RED),
}

log = logging.getLogger(__name__)


# call logging
def call_log(api_name, api_url, call_params, return_data):
    return '''
Call %s ------------->
URL:
    %s
Params:
    %s
Return:
    %s
-------------------%s<''' % (api_name, api_url, call_params, return_data, '-'*len(api_name))


def class_name_to_api_name(class_name):
    api_name = class_name[0].lower()
    for char in class_name[1:]:
        if char in string.ascii_uppercase:
            api_name += '_' + char.lower()
        else:
            api_name += char
    return api_name


def load_yaml(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    conf = yaml.load(f)
    f.close()
    return conf


def multiply(expression):
    """multiplication calculation

    :param expression: string e.g. "1024*1024*50"
    :return: integer
    """
    value = 1
    for n in expression.split('*'):
        value *= int(n)
    return value
    # sympy takes up too much memory
    # from sympy.parsing.sympy_parser import parse_expr
    # return int(parse_expr(expression).evalf())


class CustomizeHelpFormatter(HelpFormatter):
    """Customize ArgumentParser's Help info """

    def add_usage(self, usage, actions, groups, prefix=None):
        sys.stdout.write('%s%s%s' % (usage, os.linesep, os.linesep))

    def format_help(self):
        return None


def format_level_name(level_name):
    if level_name == 'WARNING':
        return 'WARN '
    elif level_name == 'CRITICAL':
        return 'FATAL'
    return level_name.ljust(5)


class CustomizeLog(logging.Formatter):
    def __init__(self, fmt=None, date_fmt=None, width_color=False):
        self.width_color = width_color
        logging.Formatter.__init__(self, fmt, date_fmt)

    def format(self, record):
        record.levelname = format_level_name(record.levelname)
        if self.width_color:
            fg_color, bg_color = LEVEL_COLOR_MAPPING[record.levelno]
            record.levelname = COLOR_PATTERN % (30 + fg_color, 40 + bg_color, record.levelname)
        return logging.Formatter.format(self, record)


def set_logging(config, root_path=''):
    """setting logging

    :param config: config dict
    :param root_path:
    """
    colour = config['class']['stream']['colour']        # windows not support
    default_format = CustomizeLog(config['format'])
    stream_format = CustomizeLog(config['format'], width_color=True) if colour and POSIX else default_format
    handlers = {}

    # console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(stream_format)
    handlers['stream'] = handler

    # customize handler
    for handler_name, params in config['handler'].items():
        handler_format = CustomizeLog(params['format']) if params.get('format') else default_format
        handler_params = config['class'][params['class']].copy()
        handler_params.update(params)
        # create log dir
        logfile = params['path'] if params['path'].startswith('/') else os.path.join(root_path, params['path'])
        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        # create handler
        backup_count = handler_params['backup_count']
        # which switches from one file to the next when the current file reaches a certain size.
        if params['class'] == 'rotating_file':
            max_size = multiply(handler_params['max_size'])
            handler = RotatingFileHandler(logfile, 'a', max_size, backup_count, encoding='utf-8')
        # rotating the log file at certain timed intervals.
        elif params['class'] == 'time_rotating_file':
            when = handler_params['when']
            interval = handler_params['interval']
            handler = TimedRotatingFileHandler(logfile, when, interval, backup_count, encoding='utf-8')
        handler.setFormatter(handler_format)
        handlers[handler_name] = handler

    for module, params in config['logger'].items():
        level = params['level'].upper()
        handler_names = params['handler'].split()
        propagate = params.get('propagate') or config['propagate']

        if module == 'default':                 # define root log
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(module)  # define module's logging
            logger.propagate = propagate        # judge whether repeatedly output to default logger

        for handler_name in handler_names:
            logger.addHandler(handlers[handler_name])
        logger.setLevel(level)


class HTMLFragmentTranslator(HTMLTranslator):

    def __init__( self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []

    def unimplemented_visit(self, node):
        pass

html_fragment_writer = Writer()
html_fragment_writer.translator_class = HTMLFragmentTranslator


def rst_to_html(source):
    html = publish_string(source, writer=html_fragment_writer)
    html = html.split(b'<div class="document">\n\n\n')[1][:-8]     # len('\n</div>\n') == 8
    if html.startswith(b'<p>'):
        html = html[3:]
    if html.endswith(b'</p>'):
        html = html[:-4]
    return html.decode()


def get_request_params(request):
    if request.method == 'GET':
        return request.args.copy().to_dict()
    else:
        if request.json is None:
            return request.form.copy().to_dict()    # Content-Type: application/x-www-form-urlencoded
        else:
            return request.json.copy()              # Content-Type: application/json


def get_cls_with_path(cls_path):
    module_name, class_name = cls_path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, class_name)


def iterate_package(package):
    for importer, modname, is_pkg in pkgutil.iter_modules(package.__path__):
        sub_package = import_module('%s.%s' % (package.__package__, modname))
        if is_pkg:
            iterate_package(sub_package)


def iterate_package_with_processor(package, processor):
    processor(package)
    for importer, modname, is_pkg in pkgutil.iter_modules(package.__path__):
        sub_package = import_module('%s.%s' % (package.__package__, modname))
        if is_pkg:
            iterate_package(sub_package, processor)
        else:
            processor(sub_package)
