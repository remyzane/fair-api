import json
from flask import session, request, render_template, Response, current_app as app
from fair import JSON, CView

from . import to_html


def index():
    api_list = []
    curr_api_context = {}
    user = request.args.get('user', '')
    context = {'user': user,
               'title': app.config['web_ui']['test_ui'].get('title', 'Test UI'),
               'web_ui_uri': app.config['web_ui']['uri'],
               'test_ui_uri': app.config['web_ui']['test_ui']['uri'],
               'post_type': request.args.get('type', 'j')}

    view_keys = list(app.view_functions.keys())
    view_keys.sort()
    for name in view_keys:
        view_class = getattr(app.view_functions[name], 'view_class', None)
        if view_class and issubclass(view_class, CView) and view_class != CView:
            methods = list(view_class.request_methods.keys())
            methods.sort()
            for method_name in methods:
                method = view_class.request_methods[method_name]
                if view_class.uri == request.args.get('api', '') and method_name == request.args.get('method', ''):
                    curr_api_context = app.config['test_ui'].get_case(user, view_class, method)
                    api_list.append((view_class.uri, method_name, to_html(method.element.title), 'active'))
                else:
                    api_list.append((view_class.uri, method_name, to_html(method.element.title), ''))
    context['api_list'] = api_list
    context.update(curr_api_context)
    return render_template('test.html', **context)


def save_case():
    result = app.config['test_ui'].save_case(**request.json)
    return Response(json.dumps(result), content_type=JSON)


def save_config():
    result = app.config['test_ui'].save_config(**request.json)
    return Response(json.dumps(result), content_type=JSON)
