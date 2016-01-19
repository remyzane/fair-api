# -*- coding: utf-8 -*-

import os
import json
from flask import session, request, render_template, Response
from curd import JSON, CView
from curd.plugin.jsonp import JsonP

from demo import app
from demo.utility import program_dir

# run in command line:
# py.test-3.x       # or
# py.test-3.x -s    # disable all capturing
#
# run in web browser:
# http://localhost:port/tests/


def _to_html(text):
    text = text.replace('&', '&#38;')
    text = text.replace(' ', '&nbsp;')
    text = text.replace(' ', '&#160;')
    # text = text.replace('<', '&#60;')
    # text = text.replace('>', '&#62;')
    text = text.replace('"', '&#34;')
    text = text.replace('\'', '&#39;')
    text = text.replace(os.linesep, '</br>')
    return text


def _get_case_dir(user, curr_api_uri, method_name):
    api_path = '_'.join(curr_api_uri[1:].split('/'))
    case_dir = os.path.realpath(os.path.join(program_dir, 'work', 'test', 'case', user, api_path, method_name))
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    return case_dir


def _get_sorted_code(user, view, method):
    codes = []
    is_param_type = False
    for error_code in method.element.code_index:
        error_message = method.element.code_dict[error_code]

        if error_code.startswith('param_type_error_') and not is_param_type:
            codes.append(('----', None, None))
            is_param_type = True

        if is_param_type and not error_code.startswith('param_type_error_'):
            codes.append(('----', None, None))
            is_param_type = False

        codes.append((error_code, _to_html(error_message),
                      _get_test_case(user, view, method, error_code)))

    return codes


def _get_test_case(user, view, method, code):
    use_cases = ''
    case_path = os.path.join(_get_case_dir(user, view.uri, method.__name__.upper()), code)
    if os.path.exists(case_path):
        data_file = open(case_path, 'r')
        for line in data_file.readlines():
            line = line.replace(os.linesep, '')
            if use_cases:
                use_cases += ', ' + line
            else:
                use_cases += line
        data_file.close()
    return '[%s]' % use_cases


# get detail info of current api
def _get_curr_api(user, view, method):
    context = dict()
    context['curr_api_uri'] = view.uri
    context['curr_api_path'] = 'http://' + request.environ['HTTP_HOST'] + view.uri
    context['curr_api_method'] = method.__name__.upper()
    context['curr_api_params'] = method.element.param_list
    context['curr_api_description'] = _to_html(method.element.description)
    context['curr_api_json_p'] = None
    context['curr_api_params_config'] = {}
    context['curr_api_codes'] = _get_sorted_code(user, view, method)
    api_config_path = os.path.join(_get_case_dir(user, view.uri, method.__name__.upper()), '__config__')
    if os.path.exists(api_config_path):
        with open(api_config_path, 'r') as config:
            api_config = json.load(config)
            context['curr_api_params_config'] = api_config['params']
    for plugin in method.element.plugins:
        if isinstance(plugin, JsonP):
            context['curr_api_json_p'] = plugin.callback_field_name
    print(method)
    print(context)
    return context


@app.route('/tests/', endpoint='tests.index')
def index():
    api_list = []
    curr_api_context = {}
    api_config = {}
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
            for _method_name, method in view_class.request_methods.items():
                api_list.append((view_class.uri, _method_name, _to_html(method.element.title)))
                if view_class.uri == request.args.get('api', '') and _method_name == request.args.get('method', ''):
                    print(view_class)
                    print(method)
                    print(view_class.request_methods)
                    curr_api_context = _get_curr_api(user, view_class, method)

    context = {'user': user,
               'api_list': api_list,
               'api_config': api_config,
               'post_type': request.args.get('type', 'j')}
    context.update(curr_api_context)
    print(context)
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
    case_path = os.path.join(_get_case_dir(user, request.json['api_path'], method_name), code)
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
    config_path = os.path.join(_get_case_dir(user, request.json['api_path'], method_name), '__config__')

    data = request.json.copy()
    del data['user']
    del data['api_path']

    # save configure
    data_file = open(config_path, 'w')
    data_file.write(json.dumps(data))
    data_file.close()

    return Response(json.dumps({'result': 'success'}), content_type=JSON)
