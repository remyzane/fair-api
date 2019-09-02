import os
import string
import logging
import pkgutil
from flask import request
from importlib import import_module
from docutils.core import publish_string
from docutils.writers.html4css1 import Writer, HTMLTranslator

log = logging.getLogger(__name__)


class ContextClass(object):
    """ Context Class
    ab = ContextClass(a=1, b=2)      ab.__dict__  # {'a': 1, 'b': 2}
    """
    def __init__(self, **params):
        for key, value in params.items():
            setattr(self, key, value)

    @property
    def __data__(self):
        data = self.__dict__
        for key, value in data.items():
            if isinstance(value, ContextClass):
                data[key] = value.__data__
        return data


def request_args(arg, default_value=None):
    """ request parameter getter
    """
    if request.method == 'GET':
        return request.args.get(arg, default_value)
    else:   # POST
        # get from url
        value = request.args.get(arg)
        if value:
            return value
        else:
            if request.json is None:
                # Content-Type: application/x-www-form-urlencoded
                return request.form.get(arg, default_value)
            else:
                # Content-Type: application/json
                return request.json.get(arg, default_value)


# call logging
def call_log(api_name, api_url, call_params, return_data):
    return '''
Call %s ------------->
URL:
    %s
Params:
    %s
Return:
    %s
-------------------%s<''' % (api_name, api_url, call_params, return_data, '-'*len(api_name))


def class_name_to_api_name(class_name):
    api_name = class_name[0].lower()
    for char in class_name[1:]:
        if char in string.ascii_uppercase:
            api_name += '_' + char.lower()
        else:
            api_name += char
    return api_name


class HTMLFragmentTranslator(HTMLTranslator):

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []

    def unimplemented_visit(self, node):
        pass


html_fragment_writer = Writer()
html_fragment_writer.translator_class = HTMLFragmentTranslator


def rst_to_html(source):
    if not source:
        return ''
    html = publish_string(source, writer=html_fragment_writer)
    html = html.split(b'<div class="document">\n\n\n')[1][:-8]     # len('\n</div>\n') == 8
    if html.startswith(b'<p>'):
        html = html[3:]
    if html.endswith(b'</p>'):
        html = html[:-4]
    return html.decode()


def text_to_html(text):
    text = text.replace('&', '&#38;')
    text = text.replace(' ', '&nbsp;')
    text = text.replace(' ', '&#160;')
    # text = text.replace('<', '&#60;')
    # text = text.replace('>', '&#62;')
    text = text.replace('"', '&#34;')
    text = text.replace('\'', '&#39;')
    text = text.replace(os.linesep, '</br>')
    return text


def get_request_params(request):
    if request.method == 'GET':
        return request.args.copy().to_dict()
    else:
        if request.json is None:
            return request.form.copy().to_dict()    # Content-Type: application/x-www-form-urlencoded
        else:
            return request.json.copy()              # Content-Type: application/json


def get_cls_with_path(cls_path):
    module_name, class_name = cls_path.rsplit(".", 1)
    _module = import_module(module_name)
    return getattr(_module, class_name)


def iterate_package(package):
    for importer, modname, is_pkg in pkgutil.iter_modules(package.__path__):
        sub_package = import_module('%s.%s' % (package.__package__, modname))
        if is_pkg:
            iterate_package(sub_package)


def structure_params(view_func, params_proto, params):

    # check the necessary parameter's value is sed
    for param in view_func.meta.param_not_null:
        if params_proto.get(param, '') == '':       # 0 is ok
            raise view_func.meta.response('param_missing', {'parameter': param})

    ret = view_func.meta.param_default.copy()
    # parameter's type of proof and conversion
    for param, value in params.items():
        if param not in view_func.meta.param_index:
            raise view_func.meta.response('param_unknown', {'parameter': param, 'value': value})
        if value is not None:
            try:
                ret[param] = view_func.meta.param_types[param].structure(view_func, value)
            except Exception as e:
                raise view_func.meta.response(view_func.meta.param_types[param].error_code, {'parameter': param, 'value': value})
    return ret
