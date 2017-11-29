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
    """Json response

    format: { "code": "", "info": "",  "data": "" }
    """

    def response(self):
        ret = {'code': self.code, 'info': self.view.codes[self.code], 'data': self.data}
        return self.code, ret, Response(json.dumps(ret), content_type=JSON, status=self.status)
