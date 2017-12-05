from flask import Flask, request

from . import ui
from .air import Air, set_view_func
from .utility import request_args


class Fair(Flask):
    """ """

    def __init__(self, import_name, **kwargs):
        super(Fair, self).__init__(import_name, **kwargs)
        self.air = Air(self)

    def route(self, url=None, **options):

        def decorator(view_func):
            endpoint = options.pop('endpoint', url)

            self.add_url_rule(url, endpoint, view_func, **options)

            set_view_func(self, view_func, endpoint)

            return view_func

        return decorator

    def preprocess_request(self):
        # 404: None    static: flask.helpers._PackageBoundObject.send_static_file
        view_func = self.view_functions.get(request.endpoint)
        return super(Fair, self).preprocess_request()

    def dispatch_request(self):
        # 404: None    static: flask.helpers._PackageBoundObject.send_static_file
        view_func = self.view_functions.get(request.endpoint)
        print(request.endpoint)
        print(view_func)
        response_accept = request.headers.get('Accept')
        # if 'text/html' in response_accept:
        sign = request_args('fair')
        print(sign)
        if sign:
            return ui.adapter(view_func, sign)

        response = super(Fair, self).dispatch_request()
        return response
