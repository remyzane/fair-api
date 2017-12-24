from flask import Flask, request

from . import ui
from .air import Air
from .element import Element
from .utility import request_args


class Fair(Flask):
    """ """

    def __init__(self, import_name, **kwargs):
        tests_storage = kwargs.pop('tests_storage', None)
        self.tests_storage = kwargs.pop('tests_storage', None)
        super(Fair, self).__init__(import_name, **kwargs)
        self.air = Air(self, tests_storage=tests_storage)

    def route(self, rule=None, **options):

        def decorator(view_func):
            self.air_decorator(rule, view_func, **options)
            return view_func

        return decorator

    def preprocess_request(self):
        # 404: None    static: flask.helpers._PackageBoundObject.send_static_file
        view_func = self.view_functions.get(request.endpoint)

        return super(Fair, self).preprocess_request()

    def dispatch_request(self):
        # 404: None    static: flask.helpers._PackageBoundObject.send_static_file
        view_func = self.view_functions.get(request.endpoint)
        # response_accept = request.headers.get('Accept')
        # if 'text/html' in response_accept:
        sign = request_args('fair')
        if sign:
            return ui.adapter(view_func, sign)

        response = super(Fair, self).dispatch_request()
        return response

    def air_decorator(self, rule, view_func, **options):

        endpoint = self.set_view_func(self, view_func, rule, options)

        self.add_url_rule(rule, endpoint, view_func, **options)

    def set_view_func(self, view_func, rule, options):
        http_methods = options.get('methods', None)

        # convert methods string to duple, e.g. 'post'  ->  ('POST',)
        if http_methods and type(http_methods) == str:
            options['methods'] = (http_methods.upper(),)

        endpoint = options.pop('endpoint', rule)

        view_func.element = Element(self.air, view_func, http_methods)   # type: Element
