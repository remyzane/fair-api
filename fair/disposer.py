import os
import logging
import docutils
from docutils.core import publish_doctree

from .setts import Setts
from .parameter import Param, List
from .utility import rst_to_html

log = logging.getLogger(__name__)


# def method_filter(view_func):
# def get_method_list(view_func):
#     element = view_func.element
#     ret = []
#     for method in methods:
#         if method not in ('OPTIONS', 'HEAD'):
#             ret.append(method)
#     ret.sort()
#     return set(ret)


class Disposer(object):
    """ API Disposer

    Generate element info through view's doc string

    element: {
        title: 'xxx',
        description: 'description',
        response: response,
        plugins: (class_A, class_B),
        plugin_keys: ('plugin_a', 'plugin_b'),
        param_not_null: ('xx', 'yy'),
        param_allow_null: ('zz',),
        param_index: ('xx', 'yy', 'zz'),
        param_list: (
            {
                name: xxx,
                type: class_A,
                requisite: True/False,
                description: 'xxx'
            },
            ...
        ),
        param_dict: {
            xxx: {
                name: xxx,
                type: class_A,
                requisite: True/False,
                description: 'description'
            },
            ...
        },
        param_default: {
            'xx': None,
            'yy': None,
            'zz': None
        }
        code_index: ('xx', 'yy', 'zz'),
        code_list: (
            ('xx', 'xxx', 'common'),
            ('yy', 'yyy', 'plugin'),
            ('zz', 'zzz', 'type'),
            ('aa', 'aaa', 'biz')
        )
        code_dict: {
            'xx': 'xxx',
            'yy': 'yyy',
            'zz': 'zzz'
        }
    }
    """
    # title = None
    #
    # description = None
    #
    # response = None
    #
    # plugin = None
    #
    # param_list = None
    #
    # param_dict = None
    #
    # param_index = None
    #
    # param_default = None
    #
    # param_not_null = None
    #
    # param_allow_null = None
    #
    # param_types = None
    #
    # code_index = None
    #
    # code_dict = None

    def __init__(self, setts, view_func, rule, http_methods):
        self.setts = setts                                  # type: Setts
        self.rule = rule
        self.http_methods = http_methods    # type: tuple
        self.title = ''
        self.description = None
        self.response = None
        self.plugins = []
        self.plugin_keys = []
        self.param_list = []
        self.param_dict = {}
        self.param_index = []
        self.param_default = {}
        self.param_not_null = []
        self.param_allow_null = []
        self.param_types = {}
        self.code_index = []
        self.code_list = []
        self.code_dict = {}
        self.__code_set('success', 'Success', 'common')
        self.__code_set('exception', 'Unknown exception', 'common')
        self.__code_set('param_unknown', 'Unknown parameter', 'common')
        if not view_func.__doc__:
            raise Exception('%s doc not defined' % view_func.__name__)
        try:
            doc_string = view_func.__doc__
            doc_tree = publish_doctree(doc_string)
            self.__parse_doc_tree(view_func, doc_tree)
            self.__clear_up()
        except Exception:
            log.exception('element defined error')

        for plugin in self.plugins:
            plugin.init_view(setts, view_func, rule, http_methods)
            # add plugin.parameters to method.element.param_list.
            if plugin.parameters:
                plugin_parameters = list(plugin.parameters)
                param_list = list(self.param_list)
                while plugin_parameters:
                    p = plugin_parameters.pop()
                    param_list.insert(0, {'name': p[0], 'type': p[1], 'requisite': p[2], 'description': p[3]})
                self.param_list = tuple(param_list)

    def __clear_up(self):
        if self.param_not_null:
            self.code_index.insert(2, 'param_missing')
            self.code_list.insert(2, ('param_missing', 'Missing parameter', 'common'))
            self.code_dict['param_missing'] = 'Missing parameter'
        self.plugins = tuple(self.plugins)
        self.plugin_keys = tuple(self.plugin_keys)
        self.param_list = tuple(self.param_list)
        self.param_not_null = tuple(self.param_not_null)
        self.param_allow_null = tuple(self.param_allow_null)
        self.param_index = self.param_not_null + self.param_allow_null
        self.code_index = tuple(self.code_index)
        self.code_list = tuple(self.code_list)
        self.response = self.response or self.air.responses['default']
        self.description = self.description or ''

    def __code_set(self, error_code, error_message, category='biz'):
        if error_code not in self.code_index:
            self.code_index.append(error_code)
            self.code_list.append((error_code, error_message, category))
            self.code_dict[error_code] = error_message

    def __parse_doc_tree(self, view_func, doc_tree):
        if type(doc_tree) == docutils.nodes.term:
            self.title = rst_to_html(doc_tree.rawsource)
            return

        if type(doc_tree) == docutils.nodes.paragraph:
            if self.description is None:
                self.title = self.title + rst_to_html(doc_tree.rawsource)
                self.description = ''
            elif self.description == '':
                self.description = rst_to_html(doc_tree.rawsource)
            else:
                self.description = self.description + os.linesep * 2 + rst_to_html(doc_tree.rawsource)
            return

        if type(doc_tree) == docutils.nodes.field:
            self.__parse_doc_field(view_func, doc_tree)
            return

        for item in doc_tree.children:
            self.__parse_doc_tree(view_func, item)

    def __parse_doc_field(self, view_func, doc_field):
        name = doc_field.children[0].astext()
        content = rst_to_html(doc_field.children[1].rawsource)
        if name == 'response':
            self.response = self.air.responses[content]
        elif name == 'plugin':
            for item in content.split():
                plugin = self.air.plugins.get(item)
                if not plugin:
                    raise Exception('%s use undefined plugin %s' % (view_func.__name__, item))
                self.plugins.append(plugin)
                self.plugin_keys.append(item)
                for error_code, error_message in plugin.error_codes.items():
                    self.__code_set(error_code, error_message, 'plugin ' + item)
        elif name.startswith('raise '):
            self.__code_set(name[6:], content)
        elif name.startswith('param '):
            items = name[6:].split()
            param_type = items[0]
            if param_type.endswith(']'):
                sub_type = self.air.parameter_types.get(param_type.split('[')[1][:-1])
                param_type = self.air.parameter_types.get(param_type.split('[')[0])
                param_type = param_type(sub_type)
            else:
                param_type = self.air.parameter_types.get(param_type)
            if not param_type:
                error = '%s.%s use undefined parameter type %s'
                raise Exception(error % (self.__name__, view_func.__name__, items[0]))
            for request_method in self.http_methods:
                if request_method not in ('HEAD', 'OPTIONS'):
                    if request_method not in param_type.support:
                        error = 'parameter %s not support http %s method in %s'
                        raise Exception(error % (param_type.__name__, request_method, self.rule))

            param = {'name': items[-1], 'type': param_type, 'requisite': False, 'description': content}
            if len(items) > 2 and items[1] == '*':
                param['requisite'] = True
                self.param_not_null.append(items[-1])
            else:
                self.param_allow_null.append(items[-1])
            self.param_list.append(param)
            self.param_dict[items[-1]] = param
            self.param_default[items[-1]] = None
            self.param_types[items[-1]] = param_type
            if isinstance(param['type'], List):
                self.__code_set(param_type.type.error_code, param_type.type.description, 'type')
                self.__code_set(param_type.error_code,
                                        param_type.description % param_type.type.__name__, 'type')
            elif param['type'] != Param:
                self.__code_set(param_type.error_code, param_type.description, 'type')
        else:
            setattr(self, name, content)
