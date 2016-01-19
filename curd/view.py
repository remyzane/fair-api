# -*- coding: utf-8 -*-

import logging
from flask.views import request
from flask import Response

from .configure import db
from .element import Element
from .response import ResponseRaise, JsonRaise
from .utility import get_request_params

log = logging.getLogger(__name__)

_request_params_log = '''
Request Params: -----------------------------------------
%s
---------------------------------------------------------'''


class CView(object):
    """View base class
    """
    uri = None
    request_methods = None
    # # Can be overload by subclasses
    # database = 'default'        # used by auto_rollback
    # db = None
    # auto_rollback = True       # auto rollback the current transaction while result code != success
    # parameters = {}             # example：{'Id': Int, ...}, type has available：Int, Float, Str, Mail、...
    # requisite = []
    # json_p = None               # if defined view's return will using jsonp (accustomed to using 'callback')
    # codes = None
    # plugins = None
    # exclude = ()

    @classmethod
    def __request_methods(cls, view_wrapper):
        cls.request_methods = {}
        for method_name in ['get', 'post', 'head', 'options', 'delete', 'put', 'trace', 'patch']:
            if hasattr(cls, method_name):
                cls.request_methods[method_name.upper()] = getattr(cls, method_name)
        view_wrapper.methods = cls.request_methods.keys()

    @classmethod
    def __reconstruct(cls, app, uri, view_wrapper):
        cls.uri = uri
        cls.__request_methods(view_wrapper)
        for method in cls.request_methods.values():
            method.element = Element(app, cls, method)
            for plugin in method.element.plugins:
                plugin.init_view(cls, method)

        # setting database
        # cls.db = db.get(cls.database)

    def __init__(self):
        # the following variables is different in per request
        self.request = request
        self.application_json = False if request.json is None else True     # Content-Type: application/json
        self.method = self.request_methods[request.method]
        self.element = self.method.element
        self.raise_response = self.element.response
        self.types = self.element.param_types
        self.codes = self.element.code_dict
        self.params = {}
        self.params_proto = {}
        self.params_log = ''
        self.process_log = ''

    def __response(self, *args, **kwargs):
        try:
            # get request parameters
            self.params = get_request_params(request)
            self.params_proto = self.params.copy()

            # plugin
            for plugin in self.element.plugins:
                plugin.before_request(self)

            # structure parameters
            self.__structure_params()

            response_content = self.method(self, **self.params)
            if type(response_content) == tuple:
                code, content, response_content = response_content
                self.log(code, content)
            else:
                self.log('success', response_content)
        except ResponseRaise as response_raise:
            code, content, response_content = response_raise.response()
            self.log(code, content)
        except Exception:
            code, content, response_content = self.r('exception')
            self.log(code, content, True)
        return response_content

    @classmethod
    def as_view(cls, name, uri, app, *class_args, **class_kwargs):
        def view_wrapper(*args, **kwargs):
            # instantiate view class, thread security
            self = view_wrapper.view_class(*class_args, **class_kwargs)
            # rollback the current transaction while result code != success
            # if self.auto_rollback:
            #     with self.db.transaction():
            #         return self.dispatch_request(*args, **kwargs)
            # else:
            #     return self.dispatch_request(*args, **kwargs)
            ret = self.__response(*args, **kwargs)
            return ret

        view_wrapper.view_class = cls
        view_wrapper.__name__ = name
        view_wrapper.__module__ = cls.__module__
        view_wrapper.__doc__ = cls.__doc__
        # reconstruct view class
        cls.__reconstruct(app, uri, view_wrapper)
        return view_wrapper

    # get request parameters
    def __structure_params(self):

        self.params_log = _request_params_log % self.params

        # check the necessary parameter's value is sed
        for param in self.element.param_not_null:
            if self.params_proto.get(param, '') == '':       # 0 is ok
                raise JsonRaise(self, 'param_missing', {'parameter': param})

        params = self.element.param_default.copy()

        # parameter's type of proof and conversion
        for param, value in self.params.items():
            if param not in self.element.param_index:
                raise JsonRaise(self, 'param_unknown', {'parameter': param, 'value': value})

            if value is not None:
                params[param] = self.types[param].structure(self, value)
                #
                # # type conversion (application/json don't need) (Str and its subclasses don't need)
                # if not issubclass(_type, Str):
                #     try:
                #         value = _type.conversion(value) if value else None
                #         self.params[param] = value
                #     except ValueError:
                #         raise RR(self.response(_type.code, {'parameter': param, 'value': value}))
                # # parameter check
                # error_code = _type.check(value)
                # if error_code:
                #     raise RR(self.response(error_code, {'parameter': param, 'value': value}))
        self.params = params

    def r(self, code, data=None, status=None):
        return self.raise_response(self, code, data, status).response()

    def rr(self, code, data=None, status=None):
        """Raise response

        :return:
        """
        return self.raise_response(self, code, data, status)

    def log(self, code, response_content, exception=False):
        if self.process_log:
            self.process_log = '''
Process Flow: -------------------------------------------
%s
---------------------------------------------------------''' % self.process_log
        debug_info = '''%s
Return Data: --------------------------------------------
%s
---------------------------------------------------------''' % (self.process_log, str(response_content))
        if code == 'success':
            # different log output for performance
            if log.parent.level == logging.DEBUG:
                log.info('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.info('%s %s %s', request.path, self.codes[code], self.params_log)
        else:
            if exception:
                print('%s %s %s %s' % (request.path, self.codes[code], self.params_log, debug_info))
                log.exception('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
                # log.exception('')
            else:
                log.error('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
