import json
from flask import Response
from http_api.plugin import Plugin
from http_api.response import ResponseRaise, JSON_P


class JsonPRaise(ResponseRaise):
    """Json response

    format: { "code": "", "message": "",  "data": "" }
    """

    def response(self):
        ret = {'code': self.code, 'message': self.view.codes[self.code], 'data': self.data}
        content = self.view.json_p_callback_name + '(' + json.dumps(ret) + ')'
        return self.code, ret, Response(content, content_type=JSON_P, status=self.status)


class JsonP(Plugin):
    """Jsonp response Plugin

    if defined in view's return will using jsonp (accustomed to using 'callback')
    """
    error_codes = {}

    def __init__(self, params):
        self.callback_field_name = params['callback_field_name']

    def init_view(self, view_class, method):
        if method.__name__ is not 'get':
            raise Exception('Error define in %s.%s: json_p plugin only support GET method.' %
                            (view_class.__name__, method.__name__))

    def before_request(self, view):
        if self.callback_field_name in view.params:
            view.json_p_callback_name = view.params[self.callback_field_name]
            view.raise_response = JsonPRaise
            del view.params[self.callback_field_name]
            if '_' in view.params:
                del view.params['_']
            if '1_' in view.params:
                del view.params['1_']
