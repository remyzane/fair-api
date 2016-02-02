import os
import logging
import docutils
from docutils.core import publish_doctree

from .parameter import Param, List
from .utility import rst_to_html

log = logging.getLogger(__name__)


class Element(object):
    """
        element: {
        title: 'xxxxx',
        description: 'xxxxxx',
        response: response,
        plugins: (class_A, class_B),
        param_not_null: ('xx', 'yy'),
        param_allow_null: ('zz',),
        param_index: ('xx', 'yy', 'zz'),
        param_list: (
            {
                name: xxx,
                type: class_A,
                requisite: True/False,
                description: 'xxxxx'
            },
            ...
        ),
        param_dict: {
            xxx: {
                name: xxx,
                type: class_A,
                requisite: True/False,
                description: 'xxxxx'
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
            ('xx', 'xxxxxxx'),
            ('yy', 'yyyyyyy'),
            ('zz', 'zzzzzzz')
        )
        code_dict: {
            'xx': 'xxxxxxx',
            'yy': 'yyyyyyy',
            'zz': 'zzzzzzz'
        }
    """
    title = None

    description = None

    response = None

    plugin = None

    param_list = None

    param_dict = None

    param_index = None

    param_default = None

    param_not_null = None

    param_allow_null = None

    param_types = None

    code_index = None

    code_dict = None

    def __init__(self, app, view, method):
        self.title = ''
        self.plugins = []
        self.param_list = []
        self.param_dict = {}
        self.param_index = []
        self.param_default = {}
        self.param_not_null = []
        self.param_allow_null = []
        self.param_types = {}
        self.code_index = ['success', 'exception', 'param_unknown', 'param_missing']
        self.code_list = []
        self.code_dict = {
            'success': 'Success',
            'exception': 'Unknown exception',
            'param_unknown': 'Unknown parameter',
            'param_missing': 'Missing parameter'
        }
        if not method.__doc__:
            raise Exception('%s.%s doc not undefined' % (view.__name__, method.__name__))
        try:
            doc_field = publish_doctree(method.__doc__)
            self.__parse_doc_tree(app, view, method, doc_field)
            self.__clear_up(app)
        except Exception:
            log.exception('element defined error')

    def __clear_up(self, app):
        if not self.param_not_null:
            self.code_index.remove('param_missing')
            del self.code_dict['param_missing']
        self.plugins = tuple(self.plugins)
        self.param_list = tuple(self.param_list)
        self.param_not_null = tuple(self.param_not_null)
        self.param_allow_null = tuple(self.param_allow_null)
        self.param_index = self.param_not_null + self.param_allow_null
        self.code_index = tuple(self.code_index)
        code_list = []
        for code in self.code_index:
            code_list.append((code, self.code_dict[code]))
        self.code_list = tuple(code_list)
        self.response = self.response or app.config['responses']['default']
        self.description = self.description or ''

    def __element_code_set(self, error_code, error_message):
        if error_code not in self.code_index:
            self.code_index.append(error_code)
            self.code_dict[error_code] = error_message

    def __parse_doc_field(self, app, view, method, doc_field):
        name = doc_field.children[0].astext()
        content = rst_to_html(doc_field.children[1].rawsource)
        if name == 'response':
            self.response = app.config['responses'][content]
        elif name == 'plugin':
            for item in content.split():
                plugin = app.config['plugins'].get(item)
                if not plugin:
                    raise Exception('%s.%s use undefined plugin %s' % (view.__name__, method.__name__, item))
                self.plugins.append(plugin)
                for error_code, error_message in plugin.error_codes.items():
                    self.__element_code_set(error_code, error_message)
        elif name.startswith('raise '):
            self.__element_code_set(name[6:], content)
        elif name.startswith('param '):
            items = name[6:].split()
            param_type = items[0]
            if param_type.endswith(']'):
                sub_type = app.config['parameter_types'].get(param_type.split('[')[1][:-1])
                param_type = app.config['parameter_types'].get(param_type.split('[')[0])
                param_type = param_type(sub_type)
            else:
                param_type = app.config['parameter_types'].get(param_type)
            if not param_type:
                raise Exception('%s.%s use undefined parameter type %s' % (self.__name__, method.__name__, items[0]))
            if method.__name__.upper() not in param_type.support:
                raise Exception('%s.%s use parameter %s type that not support %s method.' %
                                (self.__name__, method.__name__, param_type.__name__, method.__name__.upper()))
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
                self.__element_code_set(param_type.type.error_code, param_type.type.description)
                self.__element_code_set(param_type.error_code, param_type.description % param_type.type.__name__)
            elif param['type'] != Param:
                self.__element_code_set(param_type.error_code, param_type.description)
        else:
            setattr(self, name, content)

    def __parse_doc_tree(self, app, view, method, doc_tree):
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
            self.__parse_doc_field(app, view, method, doc_tree)
            return

        for item in doc_tree.children:
            self.__parse_doc_tree(app, view, method, item)
