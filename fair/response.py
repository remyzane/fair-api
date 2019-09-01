import json
import logging
from flask import Response

log = logging.getLogger(__name__)

JSON = 'application/json; charset=utf-8'
JSON_P = 'application/javascript; charset=utf-8'


class ResponseRaise(Exception):

    def __init__(self, api, code, data=None, status=None):
        self.api = api
        self.code = code
        self.info = api.code_dict[code]
        self.data = data
        self.status = status

    def response(self):
        raise NotImplementedError()


class JsonRaise(ResponseRaise):
    """Json format：{ "code": "", "info": "",  "data": ... } """   # 请勿修改该 doc str，doc_ui 界面要使用

    def response(self):
        ret = {'code': self.code, 'info': self.info, 'data': self.data}
        return self.code, ret, Response(json.dumps(ret), content_type=JSON, status=self.status)
