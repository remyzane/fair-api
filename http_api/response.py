import json
import logging
from flask import Response

log = logging.getLogger(__name__)

JSON = 'application/json; charset=utf-8'
JSON_P = 'application/javascript; charset=utf-8'


class ResponseRaise(Exception):

    def __init__(self, view, code, data=None, status=None):
        self.view = view
        self.code = code
        self.data = data
        self.status = status

    def response(self):
        raise NotImplementedError()


class JsonRaise(ResponseRaise):

    def response(self):
        ret = {'code': self.code, 'message': self.view.codes[self.code], 'data': self.data}
        return self.code, ret, Response(json.dumps(ret), content_type=JSON, status=self.status)


class JsonPRaise(ResponseRaise):

    def response(self):
        ret = {'code': self.code, 'message': self.view.codes[self.code], 'data': self.data}
        content = self.view.json_p_callback_name + '(' + json.dumps(ret) + ')'
        return self.code, ret, Response(content, content_type=JSON_P, status=self.status)
