import json
from flask import Response, request
from ..api_setts import Setts
from ..api_meta import Meta
from ..plugin import Plugin
from ..response import ResponseRaise, JSON_P
from ..utility import get_request_params


class JsonPRaise(ResponseRaise):
    """Json format：{ "code": "", "info": "",  "data": ... } """   # 请勿修改该 doc str，doc_ui 界面要使用

    def response(self):
        ret = {'code': self.code, 'info': request.meta.code_dict[self.code], 'data': self.data}
        content = request.meta.json_p_callback_name + '(' + json.dumps(ret) + ')'
        return self.code, ret, Response(content, content_type=JSON_P, status=self.status)


class JsonP(Plugin):
    """ JsonP response Plugin

    if defined in view's return will using jsonp (accustomed to using 'callback')
    """
    error_codes = {}

    def __init__(self, callback_field_name):
        super(JsonP, self).__init__()
        self.callback_field_name = callback_field_name

    def init_view(self, setts: Setts, view_func, rule, http_methods):
        if 'GET' not in http_methods:
            raise Exception('Error define in %s: json_p plugin only support GET method.' % rule)

    def before_request(self, meta: Meta, params):
        if self.callback_field_name in params:
            meta.json_p_callback_name = params[self.callback_field_name]
            meta.raise_response = JsonPRaise
            del params[self.callback_field_name]
            if '_' in params:
                del params['_']
            if '1_' in params:
                del params['1_']
