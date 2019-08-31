import os
from flask import Blueprint
from werkzeug.routing import Rule

from .parameter import get_parameter_types
from .response import JsonRaise
from .plugin import jsonp

import logging
from importlib import import_module

from .plugin.jsonp import JsonP
from .parameter import Param
from .utility import class_name_to_api_name, iterate_package
# from .ui import setup_web_ui
from .storage import TestsLocalStorage
from .response import JsonRaise

log = logging.getLogger(__name__)


class Setts(object):
    """
        url_map define {
            url_1: {
                view_func_1: {http_method_1, http_method_2},
                view_func_2: ...
            },
            url_2: ...
        }
    """

    def __init__(self, app, browsable=True, tests_storage=None):
        self.app = app

        self.browsable = browsable

        self.url_map = dict()

        self.plugins = {'json_p': jsonp.JsonP('callback')}

        self.responses = {'default': JsonRaise}

        self.parameter_types = get_parameter_types()

        self.tests_storage = tests_storage

    def register_blueprint(self):
        templates_path = os.path.realpath(os.path.join(__file__, '..', 'ui'))
        fair_ui = Blueprint('fair_ui', __name__, template_folder=templates_path)
        self.app.register_blueprint(fair_ui)

    def register_url_map(self, url, view_func, http_methods):
        if url not in self.url_map:
            self.url_map[url] = dict()
        self.url_map[url][view_func] = http_methods

    def register_test_storage(app, test_storage=TestsLocalStorage, **params):
        """ cache_path
        """


def register_parameter(app, parameters):
    """

    :param app:
    :param parameters:
    :return:
    """


def register_plugin(app, plugins):
    """ Plugin register

    :param app: flask app
    :param plugins:
    """
    app.config['fair_plugins'] = plugins or {}


def register_response(app, responses):
    """

    :param app:
    :param responses:
    :return:
    """


