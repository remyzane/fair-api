import json
from flask import Response
from fair.plugin import Plugin
from fair.response import ResponseRaise, JSON_P


class JsonPRaise(ResponseRaise):
    """ Json Raise

    format: { "code": "", "info": "",  "data": "" }
    """

    def response(self):
        ret = {'code': self.code, 'info': self.view.codes[self.code], 'data': self.data}
        content = self.view.json_p_callback_name + '(' + json.dumps(ret) + ')'
        return self.code, ret, Response(content, content_type=JSON_P, status=self.status)


class JsonP(Plugin):
    """ JsonP response Plugin

    if defined in view's return will using jsonp (accustomed to using 'callback')
    """
    error_codes = {}

    def __init__(self, callback_field_name):
        super(JsonP, self).__init__()
        self.callback_field_name = callback_field_name

    def init_view(self, air, view_func, rule, http_methods):
        if 'GET' not in http_methods:
            raise Exception('Error define in %s: json_p plugin only support GET method.' % rule)

    def before_request(self, view):
        if self.callback_field_name in view.params:
            view.json_p_callback_name = view.params[self.callback_field_name]
            view.raise_response = JsonPRaise
            del view.params[self.callback_field_name]
            if '_' in view.params:
                del view.params['_']
            if '1_' in view.params:
                del view.params['1_']
