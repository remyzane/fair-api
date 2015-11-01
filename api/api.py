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


class RR(Exception):     # RaiseResponse
    def __init__(self, response):
        self.response = response


# api公共父类（改写自flask.views.MethodView）
class Api(object):
    # 子类可重载以下定义 (请勿在类方法中定义同名变量)
    description = ''
    db = db.get('default')      # auto_rollback 为 True 时用
    auto_rollback = True        # 是否在错误(code != 'success')时自动回滚
    parameters = {}             # 格式样例：{'Id': Int, ...}, 可用的类型有：Int, Float, Str, Mail、...
    requisite = []
    json_p = None               # 如果有指定该参数(一般使用callback)则返回jsonp
    codes = None
    plugins = None
    plugins_exclude = ()

    @classmethod
    def check_define(cls, view):
        # 判断必要参数的类型是否已定义
        for param in cls.requisite:
            if param not in cls.parameters:
                raise Exception('Error define in %s: requisite parameter [%s] not defined in parameter list.' %
                                (cls.__name__, param))
        # GET请求不支持List参数
        if hasattr(cls, 'get'):
            view.methods = ['GET']
            for _type in cls.parameters.values():
                if isinstance(_type, List):
                    raise Exception('Error define in %s: GET method not support List parameter.' % cls.__name__)
        # POST请求不支持jsonp
        elif hasattr(cls, 'post'):
            view.methods = ['POST']
            if cls.json_p:
                raise Exception('Error define in %s: POST method not support jsonp.' % cls.__name__)

    @classmethod
    def set_codes(cls):
        # 公共错误code
        cls.codes['success'] = '成功'
        cls.codes['exception'] = '未知异常'
        cls.codes['param_unknown'] = '未知参数'
        if cls.requisite:
            cls.codes['param_missing'] = '缺少参数'

        # 参数类型判断错误code
        for _type in cls.parameters.values():
            if isinstance(_type, List):
                cls.codes[_type.code] = _type.message % _type.type.__name__
                cls.codes[_type.type.code] = _type.type.message
            elif _type != Pass:
                cls.codes[_type.code] = _type.message

        # 设置plugin的code
        for _plugin in cls.plugins:
            cls.codes.update(_plugin.codes)

    @classmethod
    def init(cls):
        if cls.codes is None:
            cls.codes = {}
        if cls.plugins is None:
            cls.plugins = []

        # 设置公共plugin
        from api import app
        for plugin_path in app.config.get('plugins'):
            exec('from %s import %s as plugin' % tuple(plugin_path.rsplit('.', 1)))
            if locals()['plugin'] not in cls.plugins_exclude:
                cls.plugins.insert(0, locals()['plugin'])

        # 设置code、message
        cls.set_codes()

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        def view(*args, **kwargs):
            # 实例化请求对象(api view), 线程安全
            self = view.view_class(*class_args, **class_kwargs)
            # 自动回滚支持
            if self.auto_rollback:
                with self.db.transaction():
                    return self.dispatch_request(*args, **kwargs)
            else:
                return self.dispatch_request(*args, **kwargs)

        view.view_class = cls
        view.__name__ = name
        view.__module__ = cls.__module__
        view.__doc__ = cls.__doc__
        # 检查类定义
        cls.check_define(view)
        # 初始化类
        cls.init()
        return view

    def __init__(self):
        # 以下成员变量会根据每个请求进行设置
        self.params = {}
        self.params_log = ''
        self.process_log = ''
        self.post_json = False  # application/json -> True,  get 和 post:application/x-www-form-urlencoded -> False

    def dispatch_request(self, *args, **kwargs):
        try:
            # 获取请求参数
            self.get_request_params()
            # 参数类型和格式检查
            self.check_parameters()
            # 插件
            for plugin in self.plugins:
                plugin.do(self)
            # 分发请求
            return getattr(self, request.method.lower())(self.params, *args, **kwargs)
        except RR as e:
            return e.response
        except:
            return self.result('exception', exception=True)

    # 获取请求数据
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

    # 检查参数
    def check_parameters(self):
        # 检查必要参数是否已经设置
        for param in self.requisite:
            if self.params.get(param, '') == '':       # 为0时可以通过
                raise RR(self.result('param_missing', {'parameter': param}))
        # 参数类型转换&校样
        for param, value in self.params.items():
            _type = self.parameters.get(param)
            if not _type:
                if self.json_p:
                    # jquery 为了避免服务器端缓存会自动加上 '_', '1_' 参数,
                    # 让jquery不自动加'_'参数的方法: 设置jquery的ajax参数 cache: true
                    if param == self.json_p or param == '_' or param == '1_':
                        continue
                raise RR(self.result('param_unknown', {'parameter': param, 'value': value}))
            if value is not None:
                # 类型转换（application/json时不处理）（Str和其子类不处理）
                if not self.post_json and not issubclass(_type, Str):
                    try:
                        value = _type.conversion(value) if value else None
                        self.params[param] = value
                    except ValueError:
                        raise RR(self.result(_type.code, {'parameter': param, 'value': value}))
                # 参数校样
                error_code = _type.check(value)
                if error_code:
                    raise RR(self.result(error_code, {'parameter': param, 'value': value}))

    # 组合返回结果（HttpResponse）
    def result(self, code, data={}, status=None, exception=False):
        # 异常时自动回滚
        if self.auto_rollback and code != 'success':
            self.db.rollback()
        # 结果数据
        ret = {'code': code, 'message': self.codes[code], 'data': data}
        # 日志输出
        self.log(code, ret, exception)
        # 结果返回
        json_p = self.params.get(self.json_p) if self.json_p else None
        if json_p:
            return Response(json_p + '(' + json.dumps(ret) + ')', content_type=JSON_P, status=status)
        else:
            return Response(json.dumps(ret), content_type=JSON, status=status)

    # 输出日志
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
            # 输出调试信息，加判断是为了提高性能
            if log.parent.level == logging.DEBUG:
                log.info('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.info('%s %s %s', request.path, self.codes[code], self.params_log)
        else:
            if exception:
                log.exception('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.error('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
