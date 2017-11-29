import string
import logging
import pkgutil
from importlib import import_module
from docutils.core import publish_string
from docutils.writers.html4css1 import Writer, HTMLTranslator

log = logging.getLogger(__name__)


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
    html = publish_string(source, writer=html_fragment_writer)
    html = html.split(b'<div class="document">\n\n\n')[1][:-8]     # len('\n</div>\n') == 8
    if html.startswith(b'<p>'):
        html = html[3:]
    if html.endswith(b'</p>'):
        html = html[:-4]
    return html.decode()


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
