# -*- coding: utf-8 -*-

import os
import json
from flask import session, request, render_template, Response
from curd import JSON, CView

from demo import app
from .views_utility import to_html, get_curr_api, get_case_dir


@app.route('/tests/', endpoint='tests.index')
def index():
    api_list = []
    curr_api_context = {}
    user = request.args.get('user', '')
    if user not in app.config['tests_access_keys']:
        if app.config.get('SECRET_KEY'):
            session.pop('user', None)
        message = 'Please enter the correct access key.' if request.args.get('user') else 'Please enter the access key.'
        return render_template('tests/template/tests_auth.html', message=message)

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
    return render_template('tests/template/tests_index.html', **context)


def _params_not_equal(old_params, new_params):
    for param in old_params:
        if old_params[param] != new_params.get(param):
            return True
    for param in new_params:
        if new_params[param] != old_params.get(param):
            return True
    return False


@app.route('/tests/save_case/', endpoint='tests.save_case', methods=['POST'])
def save_case():
    user = request.json['user']
    params = request.json['params']
    param_mode = request.json['param_mode']
    method_name = request.json['method']
    code = request.json['code']

    result = []
    case_path = os.path.join(get_case_dir(user, request.json['api_path'], method_name), code)
    new_data = json.dumps({
        'param_mode': param_mode,
        'params': params
    }) + os.linesep
    # read old record
    if os.path.exists(case_path):
        data_file = open(case_path, 'r')
        for line in data_file.readlines():
            line_data = json.loads(line)
            if line_data['param_mode'] != param_mode or _params_not_equal(line_data['params'], params):
                result.append(line)
        data_file.close()
    # add new record
    result.append(new_data)

    # save the latest 10 record
    data_file = open(case_path, 'w')
    for line in result[-10:]:
        data_file.write(line)
    data_file.close()

    return Response(json.dumps({'result': 'success'}), content_type=JSON)


@app.route('/tests/save_config/', endpoint='tests.save_config', methods=['POST'])
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
