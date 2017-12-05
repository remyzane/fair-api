import os
from flask import Blueprint
from werkzeug.routing import Rule

from .parameter import get_parameter_types
from .response import JsonRaise
from .plugin import jsonp


class Air(object):
    def __init__(self, app):
        self.plugins = {'json_p': jsonp.JsonP('callback')}
        self.responses = {'default': JsonRaise}
        self.parameter_types = get_parameter_types()

        templates_path = os.path.realpath(os.path.join(__file__, '..', 'ui'))
        fair_ui = Blueprint('fair_ui', __name__, template_folder=templates_path)
        app.register_blueprint(fair_ui)


def set_view_func(app, view_func, endpoint):
    from .element import Element
    rule = app.url_map._rules_by_endpoint[endpoint][0]
    view_func.rule = rule                                   # type: Rule
    view_func.element = Element(app.air, view_func, rule)   # type: Element
