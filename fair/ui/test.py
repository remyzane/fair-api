import os
from flask import request, render_template, current_app as app
from werkzeug.routing import Rule

from fair.utility import text_to_html
from ..plugin import jsonp
from ..api_meta import Meta
from ..utility import ContextClass


def get_api_params(param_list, config):
    params = []
    params_config = config['params'] if config else {}
    for param in param_list:
        name = param['name']
        requisite = b'\xe2\x97\x8f'.decode() if param['requisite'] else ''
        if param['type'].has_sub_type:
            type_name = '%s[%s]' % (param['type'].__name__, param['type'].type.__name__)
            type_display = '''<span message="%s">%s</span>[<span message="%s">%s</span>]''' % (
                param['type'].description, param['type'].__name__,
                param['type'].type.description, param['type'].type.__name__)
        else:
            type_name = param['type'].__name__
            type_display = '''<span class="show-message" message="%s">%s</span>''' % \
                           (text_to_html(param['type'].description), param['type'].__name__)
        pure_auto = 'checked="checked"' if name in params_config and params_config[name]['pure_auto'] else ''
        param_url = params_config[name]['url'] if name in params_config else ''
        params.append((name, requisite, text_to_html(param['description']), type_name, type_display, pure_auto, param_url))
    return params


def test_ui():
    return 'aaa'
    meta = view_func.meta     # type: Meta

    c = ContextClass()
    context = {'api_config': {}, 'api_json_p': None}

    title, description = element.title, element.description
    c.url = request.path
    c.path = 'http://+ request.environ[HTTP_HOST] + view.uri'
    c.methods = []
    c.method = 'GET' or c.methods[0]
    c.params = get_api_params(element.param_list, context.get('api_config'))
    c.description = text_to_html(title + (os.linesep * 2 if description else '') + description)
    c.params_config = {}
    c.curr_api_config = {}

    for plugin in element.plugins:
        if isinstance(plugin, jsonp.JsonP):
            c.json_p = plugin.callback_field_name
    # return context



    # context = {'user': user,
    #            'title': 'Test UI',
    #            'web_ui_uri': app.config['web_ui']['uri'],
    #            'test_ui_uri': app.config['web_ui']['test_ui']['uri'],
    #            'post_type': request.args.get('type', 'j')}

    # for name in app.view_functions.keys():
    #     view_class = getattr(app.view_functions[name], 'view_class', None)
    #     if view_class and issubclass(view_class, CView) and view_class != CView:
    #         for method_name in view_class.request_methods.keys():
    #             method = view_class.request_methods[method_name]
    #             if view_class.uri == request.args.get('api', '') and method_name == request.args.get('method', ''):
    #                 curr_api_context = app.config['test_ui'].get_case(user, view_class, method)
    # context.update(curr_api_context)

    return render_template('test.html', c=c)
