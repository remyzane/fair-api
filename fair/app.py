from flask import Flask, request

from . import ui as fair_ui
from .api_setts import Setts
from .api_meta import Meta
from .ui.doc import doc_ui
from .ui.exe import exe_ui
from flask import Response
from .response import ResponseRaise
from .utility import get_request_params, structure_params


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
        if self.match():
            return self.adapter()

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

    def adapter(self):
        view_func = None
        views = self.api.url_map.get(request.path)

        for view, support_methods in views.items():
            if request.method in support_methods:
                view_func = view
                break

        if not hasattr(view_func, 'meta'):
            return Response('406 Current url not have Fair UI', status=406)

        try:
            request.meta = view_func.meta
            # get request parameters
            params = get_request_params()
            params_proto = params.copy()

            # plugin
            for plugin in view_func.meta.plugins:
                plugin.before_request(view_func.meta, params)
                for parameter in plugin.parameters:
                    del params[parameter[0]]

            # structure parameters
            params = structure_params(view_func, params_proto, params)
            response_content = view_func(**params)
            if isinstance(response_content, ResponseRaise):
                response_content = response_content.response()
        except ResponseRaise as response_raise:
            response_content = response_raise.response()
        except Exception as e:
            response_content = view_func.meta.response('exception').response()
        return response_content

    def match(self):
        """ Check fair ui whether or not shown

        keep it simple for performance
        """
        if request.path in self.api.url_map:
            for view_func, methods in self.api.url_map[request.path].items():
                if request.method in methods:
                    if self.api:
                        return True
        return False

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

        return http_methods
