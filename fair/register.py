import logging
from importlib import import_module

from .plugin.jsonp import JsonP
from .parameter import Param
from .utility import class_name_to_api_name, iterate_package
# from .ui import setup_web_ui
from .ui.test import TestsLocalStorage
from .response import JsonRaise

log = logging.getLogger(__name__)


def get_parameter_types(parameter_types=None):
    if not parameter_types:
        parameter_types = []
    parameter_types = ['fair.parameter'] + parameter_types
    types = {}
    for package_name in parameter_types:
        exec('import %s as package' % package_name)
        parameter_package = locals()['package']
        for item in dir(parameter_package):
            # flask's request and session(werkzeug.local.LocalProxy) raise RuntimeError
            if item in ['request', 'session']:
                continue
            parameter = getattr(parameter_package, item)
            try:
                if issubclass(parameter, Param):
                    if parameter.__name__ not in types:
                        types[parameter.__name__] = parameter

            except TypeError:
                pass    # Some object throw TypeError in issubclass
    return types


def default():
    fair_conf = dict()
    fair_conf['plugins'] = {'json_p': JsonP('callback')}
    fair_conf['responses'] = {'default': JsonRaise}
    fair_conf['parameter_types'] = get_parameter_types()
    return fair_conf


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

