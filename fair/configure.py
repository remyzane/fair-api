import logging
from importlib import import_module

from .parameter import Param
from .utility import class_name_to_api_name, iterate_package
from .ui import setup_web_ui
from .ui.test import TestsStandaloneUI
from .response import JsonRaise

log = logging.getLogger(__name__)


def setup(app, cache_path,
               responses=None,
               plugins=None,
               parameter_types=None):

    app.config['fair_plugins'] = plugins or {}

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
    setup_web_ui(app, web_ui_config, cache_path, TestsStandaloneUI)


def set_parameter_types(app, parameter_types):
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
    app.config['parameter_types'] = types
