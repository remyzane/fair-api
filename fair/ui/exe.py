import os
import random
from flask import request, render_template, current_app as app
from werkzeug.routing import Rule
from flask import redirect
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


def exe_ui():
    c = ContextClass()
    c.method = request.args.get('method', None)
    views = app.api.url_map[request.url_rule.rule[:-5]]
    meta = None
    for view_func in views:
        if not c.method:
            meta = view_func.meta  # type: Meta
            method = 'GET' if 'GET' in meta.http_methods else random.choice(meta.http_methods)
            return redirect(request.url_rule.rule + '?method=' + method)
        if c.method in view_func.meta.http_methods:
            meta = view_func.meta  # type: Meta
            break
    if not meta:
        return 'Http method [%s] not support' % c.method

    context = {'api_config': {}, 'api_json_p': None}

    title, description = meta.title, meta.description
    c.url = request.path
    c.path = 'http://+ request.environ[HTTP_HOST] + view.uri'
    c.params = get_api_params(meta.param_list, context.get('api_config'))
    c.title = text_to_html(title)
    c.params_config = {}
    c.curr_api_config = {}

    for plugin in meta.plugins:
        if isinstance(plugin, jsonp.JsonP):
            c.json_p = plugin.callback_field_name
    # return context



    # context = {'user': user,
    #            'title': 'Test UI',
    #            'web_ui_uri': app.config['web_ui']['uri'],
    #            'exe_ui_uri': app.config['web_ui']['exe_ui']['uri'],
    #            'post_type': request.args.get('type', 'j')}

    # for name in app.view_functions.keys():
    #     view_class = getattr(app.view_functions[name], 'view_class', None)
    #     if view_class and issubclass(view_class, CView) and view_class != CView:
    #         for method_name in view_class.request_methods.keys():
    #             method = view_class.request_methods[method_name]
    #             if view_class.uri == request.args.get('api', '') and method_name == request.args.get('method', ''):
    #                 curr_api_context = app.config['exe_ui'].get_case(user, view_class, method)
    # context.update(curr_api_context)

    return render_template('exe.html', c=c)



import json
from flask import request, render_template, Response, current_app as app
# from fair import JSON, CView



def save_case():
    result = app.config['exe_ui'].save_case(**request.json)
    return Response(json.dumps(result), content_type=JSON)


def save_config():
    result = app.config['exe_ui'].save_config(**request.json)
    return Response(json.dumps(result), content_type=JSON)




