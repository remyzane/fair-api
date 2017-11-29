import logging
from importlib import import_module

from .parameter import Param
from .utility import class_name_to_api_name, get_cls_with_path, iterate_package, rst_to_html
from .ui import setup_web_ui
from .ui.test import TestsStandaloneUI

log = logging.getLogger(__name__)


def fair_setup(app, cache_path, config, responses=None,
               plugins=None,
               parameter_types=None):

    app.config['fair_plugins'] = plugins or {}

    # configure flask app
    setup_config(app, config)

    # set parameter types
    set_parameter_types(app, parameter_types)

    # configure view
    setup_view(app, config['app'].get('view_packages', ()))

    # configure web ui
    setup_web_ui(app, config['app']['web_ui'], cache_path, TestsStandaloneUI)


def setup_config(app, config):
    """Configure flask app.

    :param app: Flask app object
    :param config: api's config
    :type  config: dict
    """
    default_class_sign = ''
    app.config['responses'] = app.config.get('responses') or {}
    for name, class_path in app.config['responses'].items():
        if name == 'default':
            default_class_sign = class_path
        else:
            response_class = get_cls_with_path(class_path)
            app.config['responses'][name] = response_class
    app.config['responses']['default'] = app.config['responses'][default_class_sign]


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
def setup_view(app, config):
    """Configure view

    url route configure.

    :param app: Flask app object
    :param config: view's config
    :type  config: dict
    """
    from .view import CView

    app.jinja_env.globals.update(rst_to_html=rst_to_html)

    for package_path in config:
        iterate_package(import_module(package_path))

    for view in CView.__subclasses__():
        name = class_name_to_api_name(view.__name__)
        uri = '/%s/%s' % (view.__module__.split('.')[0], name)
        endpoint = '%s.%s' % (view.__module__.split('.')[0], name)
        app.add_url_rule(uri, view_func=view.as_view(endpoint, uri, app))
