import os
from flask import Blueprint
from werkzeug.routing import Rule

from .parameter import get_parameter_types
from .response import JsonRaise
from .plugin import jsonp


class Air(object):
    def __init__(self, app, tests_storage=None):
        self.plugins = {'json_p': jsonp.JsonP('callback')}
        self.responses = {'default': JsonRaise}
        self.parameter_types = get_parameter_types()
        self.tests_storage = tests_storage

        templates_path = os.path.realpath(os.path.join(__file__, '..', 'ui'))
        fair_ui = Blueprint('fair_ui', __name__, template_folder=templates_path)
        app.register_blueprint(fair_ui)
