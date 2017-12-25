import os
from flask import Blueprint
from werkzeug.routing import Rule

from .parameter import get_parameter_types
from .response import JsonRaise
from .plugin import jsonp


class Air(object):
    """
        url_map define {
            url_1: {
                view_func_1: {http_method_1, http_method_2},
                view_func_2: ...
            },
            url_2: ...
        }
    """

    def __init__(self, app, tests_storage=None):

        self.url_map = dict()

        self.plugins = {'json_p': jsonp.JsonP('callback')}

        self.responses = {'default': JsonRaise}

        self.parameter_types = get_parameter_types()

        self.tests_storage = tests_storage

        templates_path = os.path.realpath(os.path.join(__file__, '..', 'ui'))
        fair_ui = Blueprint('fair_ui', __name__, template_folder=templates_path)
        app.register_blueprint(fair_ui)

    def set_url_map(self, url, view_func, http_methods):
        if url not in self.url_map:
            self.url_map[url] = dict()
        self.url_map[url][view_func] = http_methods
