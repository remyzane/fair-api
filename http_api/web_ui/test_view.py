# -*- coding: utf-8 -*-

import os
import json
from flask import session, request, render_template, Response, current_app as app
from http_api import JSON, CView

from .test_ui import to_html, get_curr_api, get_case_dir


def index():
    app.config['test_ui'].get_case()
    api_list = []
    curr_api_context = {}
    user = request.args.get('user', '')
    if user not in app.config['tests_access_keys']:
        if app.config.get('SECRET_KEY'):
            session.pop('user', None)
        message = 'Please enter the correct access key.' if request.args.get('user') else 'Please enter the access key.'
        return render_template('tests_auth.html', message=message)

    if app.config.get('SECRET_KEY'):
        session['user'] = user

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
                    curr_api_context = get_curr_api(user, view_class, method)
                    api_list.append((view_class.uri, method_name, to_html(method.element.title), 'active'))
                else:
                    api_list.append((view_class.uri, method_name, to_html(method.element.title), ''))
    context = {'user': user,
               'api_list': api_list,
               'post_type': request.args.get('type', 'j')}
    context.update(curr_api_context)
    return render_template('tests_index.html', **context)


def save_case():
    result = app.config['test_ui'].set_case(request.json['user'],
                                            request.json['api_path'],
                                            request.json['method'],
                                            request.json['param_mode'],
                                            request.json['params'],
                                            request.json['code'])
    return Response(json.dumps(result), content_type=JSON)


def save_config():
    user = request.json['user']
    method_name = request.json['method']
    config_path = os.path.join(get_case_dir(user, request.json['api_path'], method_name), '__config__')

    data = request.json.copy()
    del data['user']
    del data['api_path']

    # save configure
    data_file = open(config_path, 'w')
    data_file.write(json.dumps(data))
    data_file.close()

    return Response(json.dumps({'result': 'success'}), content_type=JSON)
