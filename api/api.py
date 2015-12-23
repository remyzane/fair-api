# -*- coding: utf-8 -*-

import json
import logging
from flask.views import request
from flask import Response

from .configure import db
from .parameter import Pass, Str, List

log = logging.getLogger(__name__)

JSON = 'application/json; charset=utf-8'
JSON_P = 'application/javascript; charset=utf-8'

_request_params_log = '''
Request Params: -----------------------------------------
%s
---------------------------------------------------------'''


class RaiseResponse(Exception):
    def __init__(self, response):
        self.response = response

RR = RaiseResponse


# api base class（rewrite the flask.views.MethodView）
class Api(object):
    # Can be overload by subclasses
    description = ''
    database = 'default'        # used by auto_rollback
    db = None
    auto_rollback = True       # auto rollback the current transaction while result code != success
    parameters = {}             # example：{'Id': Int, ...}, type has available：Int, Float, Str, Mail、...
    requisite = []
    json_p = None               # if defined api's return will using jsonp (accustomed to using 'callback')
    codes = None
    plugins = None
    plugins_exclude = ()

    @classmethod
    def check_define(cls, view):
        # check the necessary parameter's type is defined
        for param in cls.requisite:
            if param not in cls.parameters:
                raise Exception('Error define in %s: requisite parameter [%s] not defined in parameter list.' %
                                (cls.__name__, param))
        # GET method not support List parameter
        if hasattr(cls, 'get'):
            view.methods = ['GET']
            for _type in cls.parameters.values():
                if isinstance(_type, List):
                    raise Exception('Error define in %s: GET method not support List parameter.' % cls.__name__)
        # POST method not support jsonp
        elif hasattr(cls, 'post'):
            view.methods = ['POST']
            if cls.json_p:
                raise Exception('Error define in %s: POST method not support jsonp.' % cls.__name__)

    @classmethod
    def set_codes(cls):
        # common error code
        cls.codes['success'] = 'Success'
        cls.codes['exception'] = 'Unknown exception'
        cls.codes['param_unknown'] = 'Unknown parameter'
        if cls.requisite:
            cls.codes['param_missing'] = 'Missing parameter'

        # parameter type error code
        for _type in cls.parameters.values():
            if isinstance(_type, List):
                cls.codes[_type.code] = _type.message % _type.type.__name__
                cls.codes[_type.type.code] = _type.type.message
            elif _type != Pass:
                cls.codes[_type.code] = _type.message

        # plugins error code
        for _plugin in cls.plugins:
            cls.codes.update(_plugin.codes)

    @classmethod
    def init(cls):
        if cls.codes is None:
            cls.codes = {}
        if cls.plugins is None:
            cls.plugins = []

        # setting database
        cls.db = db.get(cls.database)

        # add common plugin
        from api import app
        for plugin_path in app.config.get('plugins'):
            exec('from %s import %s as plugin' % tuple(plugin_path.rsplit('.', 1)))
            if locals()['plugin'] not in cls.plugins_exclude:
                cls.plugins.insert(0, locals()['plugin'])

        # set error code and message
        cls.set_codes()

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        def view(*args, **kwargs):
            # instantiate view class, thread security
            self = view.view_class(*class_args, **class_kwargs)
            # rollback the current transaction while result code != success
            if self.auto_rollback:
                with self.db.transaction():
                    return self.dispatch_request(*args, **kwargs)
            else:
                return self.dispatch_request(*args, **kwargs)

        view.view_class = cls
        view.__name__ = name
        view.__module__ = cls.__module__
        view.__doc__ = cls.__doc__
        # check api class define
        cls.check_define(view)
        # init api class
        cls.init()
        return view

    def __init__(self):
        # the following variables is different in per request
        self.params = {}
        self.params_log = ''
        self.process_log = ''
        self.post_json = False  # application/json -> True,  get and post:application/x-www-form-urlencoded -> False

    def dispatch_request(self, *args, **kwargs):
        try:
            # get request parameters
            self.get_request_params()
            # check parameter's type and format
            self.check_parameters()
            # plugin
            for plugin in self.plugins:
                plugin.do(self)
            # dispatch request
            return getattr(self, request.method.lower())(self.params, *args, **kwargs)
        except RR as e:
            return e.response
        except:
            return self.result('exception', exception=True)

    # get request parameters
    def get_request_params(self):
        if request.method == 'GET':
            self.params = request.args.copy()
            self.params_log = _request_params_log % self.params.to_dict()    # request.query_string
        else:
            if request.json:                            # Content-Type: application/json
                self.post_json = True
                self.params = request.json.copy()
            else:                                       # Content-Type: application/x-www-form-urlencoded
                self.params = request.form.copy()
            self.params_log = _request_params_log % self.params

    # check parameter's type and format
    def check_parameters(self):
        # check the necessary parameter's value is sed
        for param in self.requisite:
            if self.params.get(param, '') == '':       # 0 is ok
                raise RR(self.result('param_missing', {'parameter': param}))
        # parameter's type of proof and conversion
        for param, value in self.params.items():
            _type = self.parameters.get(param)
            if not _type:
                if self.json_p:
                    # jquery's cache management mechanism will add '_', '1_' parameter,
                    # let jquery don't add '_' parameter's method: set 'cache: true' in jquery's ajax method
                    if param == self.json_p or param == '_' or param == '1_':
                        continue
                raise RR(self.result('param_unknown', {'parameter': param, 'value': value}))
            if value is not None:
                # type conversion (application/json don't need) (Str and its subclasses don't need)
                if not self.post_json and not issubclass(_type, Str):
                    try:
                        value = _type.conversion(value) if value else None
                        self.params[param] = value
                    except ValueError:
                        raise RR(self.result(_type.code, {'parameter': param, 'value': value}))
                # parameter check
                error_code = _type.check(value)
                if error_code:
                    raise RR(self.result(error_code, {'parameter': param, 'value': value}))

    # get result for return（HttpResponse）
    def result(self, code, data={}, status=None, exception=False):
        # rollback the current transaction
        if self.auto_rollback and code != 'success':
            self.db.rollback()
        # data of return
        ret = {'code': code, 'message': self.codes[code], 'data': data}
        # log output
        self.log(code, ret, exception)
        # return result
        json_p = self.params.get(self.json_p) if self.json_p else None
        if json_p:
            return Response(json_p + '(' + json.dumps(ret) + ')', content_type=JSON_P, status=status)
        else:
            return Response(json.dumps(ret), content_type=JSON, status=status)

    # log output
    def log(self, code, data, exception):
        if self.process_log:
            self.process_log = '''
Process Flow: -------------------------------------------
%s
---------------------------------------------------------''' % self.process_log
        debug_info = '''%s
Return Data: --------------------------------------------
%s
---------------------------------------------------------''' % (self.process_log, str(data))
        if code == 'success':
            # different log output for performance
            if log.parent.level == logging.DEBUG:
                log.info('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.info('%s %s %s', request.path, self.codes[code], self.params_log)
        else:
            if exception:
                log.exception('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.error('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
