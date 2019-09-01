from flask import Flask, request

from . import ui as fair_ui
from .api_setts import Setts
from .api_meta import Meta
from .ui.doc import doc_ui
from .ui.exe import exe_ui


class Fair(Flask):
    """ """

    def __init__(self, import_name, **kwargs):
        api = kwargs.pop('api', None)
        super(Fair, self).__init__(import_name, **kwargs)

        self.api = api or Setts(self)                         # type: Setts
        self.api.register_blueprint()

    def route(self, rule=None, **options):

        def decorator(view_func):

            self.api_decorator(view_func, rule=rule, **options)

            return view_func

        return decorator

    def preprocess_request(self):
        # 404: None    static: flask.helpers._PackageBoundObject.send_static_file
        view_func = self.view_functions.get(request.endpoint)

        return super(Fair, self).preprocess_request()

    def dispatch_request(self):
        if fair_ui.match(self, request):
            return fair_ui.adapter(self, request)

        response = super(Fair, self).dispatch_request()
        return response

    def api_decorator(self, view_func, rule=None, **options):

        http_methods = self.api_http_method(options)

        if rule not in self.api.url_map:
            self.add_url_rule(rule + '__doc', rule + ' DOC', doc_ui)
            self.add_url_rule(rule + '__exe', rule + ' EXE', exe_ui)
        rule = self.api_rule(view_func, http_methods, rule=rule)

        endpoint = self.api_endpoint(rule, http_methods, options)

        self.add_url_rule(rule, endpoint, view_func, **options)

        view_func.meta = Meta(self.api, view_func, rule, http_methods)

    def api_rule(self, view_func, http_methods, rule=None):
        self.api.register_url_map(rule, view_func, http_methods)
        return rule

    @staticmethod
    def api_endpoint(rule, http_methods, options):
        methods = list(http_methods)
        methods.sort()
        endpoint = options.pop('endpoint', None)
        if endpoint:
            return endpoint
        return rule + ' ' + '|'.join(methods)

    @staticmethod
    def api_http_method(options):
        http_methods = options.get('methods', ('GET',))

        # convert methods string to duple, e.g. 'post'  ->  ('POST',)
        if type(http_methods) == str:
            http_methods = (http_methods.upper(),)

        # lower -> upper,  list/duple -> set
        http_methods = set(item.upper() for item in http_methods)

        options['methods'] = http_methods.copy()
        options['methods'].update(('GET',))         # add GET method for fair ui

        return http_methods
