# -*- coding: utf-8 -*-

import os
import json
import logging
import docutils
from docutils.core import publish_doctree
from flask.views import request
from flask import Response

from .configure import db
from .parameter import Param, Str, List
from .utility import rst_to_html

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


# view base class（rewrite the flask.views.MethodView）
class CView(object):
    request_methods = {}
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
        for method in ['get', 'post', 'head', 'options', 'delete', 'put', 'trace', 'patch']:
            if hasattr(cls, method):
                cls.request_methods[method.upper()] = getattr(cls, method)
        view_wrapper.methods = cls.request_methods.keys()

    @classmethod
    def __parse_doc_field(cls, app, method, element, doc_field):
        name = doc_field.children[0].astext()
        content = rst_to_html(doc_field.children[1].rawsource)
        if name == 'plugin':
            element['plugin'] = []
            for item in content.split():
                plugin = app.config['plugins'].get(item)
                if not plugin:
                    raise Exception('%s.%s use undefined plugin %s' % (cls.__name__, method.__name__, item))
                element['plugin'].append(plugin)

        elif name[:6] == 'raise ':
            element['raise'][name[6:]] = content
        elif name[:6] == 'param ':
            items = name[6:].split()
            param_type = app.config['parameter_types'].get(items[0])
            if not param_type:
                raise Exception('%s.%s use undefined parameter type %s' % (cls.__name__, method.__name__, items[0]))
            if method.__name__.upper() not in param_type.support:
                raise Exception('%s.%s use parameter %s type that not support %s method.' %
                                (cls.__name__, method.__name__, items[0], method.__name__.upper()))
            param = {'type': param_type, 'requisite': False, 'description': content}
            if len(items) > 2 and items[1] == '*':
                param['requisite'] = True
                element['essential_parameter'] = True
            element['param'][items[-1]] = param
        else:
            element[name] = content

    @classmethod
    def __parse_doc_tree(cls, app, method, element, doc_tree):
        if type(doc_tree) == docutils.nodes.term:
            element['title'] = rst_to_html(doc_tree.rawsource)
            return

        if type(doc_tree) == docutils.nodes.paragraph:
            if 'description' not in element:
                element['title'] = element.get('title', '') + rst_to_html(doc_tree.rawsource)
                element['description'] = ''
            elif element['description'] == '':
                element['description'] = rst_to_html(doc_tree.rawsource)
            else:
                element['description'] = element['description'] + os.linesep*2 + rst_to_html(doc_tree.rawsource)
            return

        if type(doc_tree) == docutils.nodes.field:
            cls.__parse_doc_field(app, method, element, doc_tree)
            return

        for item in doc_tree.children:
            cls.__parse_doc_tree(app, method, element, item)


    # @classmethod
    # def __check(cls, method):
    #     # POST method not support jsonp
    #     elif hasattr(cls, 'post'):
    #         if cls.json_p:
    #             raise Exception('Error define in %s: POST method not support jsonp.' % cls.__name__)


    @classmethod
    def __codes(cls, method):
        method.codes = dict()
        # common error code
        method.codes['success'] = 'Success'
        method.codes['exception'] = 'Unknown exception'
        method.codes['param_unknown'] = 'Unknown parameter'
        if method.element['essential_parameter']:
            method.codes['param_missing'] = 'Missing parameter'

        # parameter type error code
        for param in method.element['param'].values():
            _type = param['type']
            if isinstance(_type, List):
                method.codes[_type.error_code] = _type.requirement % _type.type.__name__
                method.codes[_type.type.error_code] = _type.type.requirement
            elif _type != Param:
                method.codes[_type.error_code] = _type.requirement

        # plugins error code
        for _plugin in method.element['plugin']:
            method.codes.update(_plugin.error_codes)

        method.codes.update(method.element['raise'])

    @classmethod
    def __reconstruct(cls, app, view_wrapper):

        cls.__request_methods(view_wrapper)

        for method in cls.request_methods.values():
            method.element = {'param': {}, 'essential_parameter': False, 'raise': {}}
            cls.__parse_doc_tree(app, method, method.element, publish_doctree(method.__doc__))
            # set error code and message
            cls.__codes(method)

        # setting database
        # cls.db = db.get(cls.database)

    @classmethod
    def as_view(cls, name, app, *class_args, **class_kwargs):
        def view_wrapper(*args, **kwargs):
            # instantiate view class, thread security
            self = view_wrapper.view_class(*class_args, **class_kwargs)
            # rollback the current transaction while result code != success
            if self.auto_rollback:
                with self.db.transaction():
                    return self.dispatch_request(*args, **kwargs)
            else:
                return self.dispatch_request(*args, **kwargs)

        view_wrapper.view_class = cls
        view_wrapper.__name__ = name
        view_wrapper.__module__ = cls.__module__
        view_wrapper.__doc__ = cls.__doc__
        # reconstruct view class
        cls.__reconstruct(app, view_wrapper)
        return view_wrapper

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
                plugin.before_request(self)
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
