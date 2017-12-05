import logging
from importlib import import_module

from .parameter import Param
from .utility import class_name_to_api_name, iterate_package
from .ui import setup_web_ui
from .ui.test import TestsLocalStorage
from .response import JsonRaise

log = logging.getLogger(__name__)


def fair_setup(app, cache_path,
               view_packages=None,
               responses=None,
               plugins=None,
               parameter_types=None):

    app.config['fair_plugins'] = plugins or {}

    app.config['responses'] = {'default': JsonRaise}

    # set parameter types
    set_parameter_types(app, parameter_types)

    # configure view
    setup_view(app, view_packages)

    # configure web ui
    web_ui_config = {
        'uri': 'api',
        'test_ui': {
            'uri': 'tests'
        }
    }
    app.config['web_ui'] = web_ui_config
    setup_web_ui(app, web_ui_config, cache_path, TestsLocalStorage)


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


# setup view url rule
def setup_view(app, view_packages):
    """Configure view

    url route configure.

    :param app: Flask app object
    :param config: view's config
    :type  config: dict
    """
    from .view_old import CView

    if not view_packages:
        return
    for package_path in view_packages:
        iterate_package(import_module(package_path))

    for view in CView.__subclasses__():
        name = class_name_to_api_name(view.__name__)
        uri = '/%s/%s' % (view.__module__.split('.')[0], name)
        endpoint = '%s.%s' % (view.__module__.split('.')[0], name)
        app.add_url_rule(uri, view_func=view.as_view(endpoint, uri, app))
