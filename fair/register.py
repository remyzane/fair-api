import logging
from importlib import import_module

from .plugin.jsonp import JsonP
from .parameter import Param
from .utility import class_name_to_api_name, iterate_package
# from .ui import setup_web_ui
from .ui.test import TestsLocalStorage
from .response import JsonRaise

log = logging.getLogger(__name__)




def register_tests(app, test_storage=TestsLocalStorage, **params):
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



def setup(app, cache_path,
               responses=None,
               plugins=None,
               parameter_types=None):



    app.config['responses'] = {'default': JsonRaise}

    # set parameter types
    set_parameter_types(app, parameter_types)

    # configure web ui
    web_ui_config = {
        'uri': 'api',
        'test_ui': {
            'uri': 'tests'
        }
    }
    app.config['web_ui'] = web_ui_config
    setup_web_ui(app, web_ui_config, cache_path, TestsLocalStorage)

