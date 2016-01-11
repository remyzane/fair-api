# -*- coding: utf-8 -*-

import os
import json
import pkgutil
from flask import session, request, render_template, Response
from curd import parameter, plugin, JSON, CView
from curd.utility import class_name_to_api_name

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


def _get_sorted_code(method_name, element, user, curr_api_uri):
    codes = []
    is_param_type = False
    for error_code in element['code_index']:
        error_message = element['code_dict'][error_code]

        if error_code.startswith('param_type_error_') and not is_param_type:
            codes.append(('----', None, None))
            is_param_type = True

        if is_param_type and not error_code.startswith('param_type_error_'):
            codes.append(('----', None, None))
            is_param_type = False

        codes.append((error_code, _to_html(error_message), _get_test_case(user, curr_api_uri, method_name, error_code)))

    return codes


def _get_test_case(user, curr_api_uri, method_name, code):
    use_cases = ''
    case_path = os.path.join(_get_case_dir(user, curr_api_uri, method_name), code)
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


@app.route('/tests/', endpoint='tests.index')
def index():
    api_list = []
    element = None
    curr_api_uri = None
    curr_api_params = []
    curr_api_codes = []
    api_config = {}
    params_config = {}
    curr_api_description = None
    request_uri = request.args.get('api', '')
    method_name = request.args.get('method', '')
    post_type = request.args.get('type', 'j')
    user = request.args.get('user', '')
    if user not in app.config['tests_access_keys']:

        if app.config.get('SECRET_KEY'):
            session.pop('user', None)

        message = 'Please enter the correct access key.' if request.args.get('user') else 'Please enter the access key.'
        return render_template('tests/template/tests_auth.html', message=message)

    if app.config.get('SECRET_KEY'):
        session['user'] = user

    for package_name in app.view_packages:
        exec('import %s as package' % package_name)
        # recursive traversal package
        for importer, modname, is_pkg in pkgutil.iter_modules(locals()['package'].__path__):
            if not is_pkg:
                exec('import %s.%s as package' % (package_name, modname))
                views = locals()['package']
                for item in dir(views):
                    view = getattr(views, item)
                    try:
                        if issubclass(view, CView) and view != CView:   # sometime issubclass throw TypeError
                            name = class_name_to_api_name(view.__name__)
                            for method_name, method in view.request_methods.items():
                                uri = '/%s/%s' % (package_name, name)
                                api_list.append((uri, method_name, _to_html(method.element['title'])))
                                if uri == request_uri:
                                    curr_api_uri = uri
                                    element = method.element
                    except TypeError:
                        pass
    # get detail info of current api
    json_p = ''
    if element:
        # json_p = curr_api_cls.json_p
        curr_api_codes = _get_sorted_code(method_name, element, user, curr_api_uri)
        api_config_path = os.path.join(_get_case_dir(user, curr_api_uri, method_name), '__config__')
        if os.path.exists(api_config_path):
            with open(api_config_path, 'r') as config:
                api_config = json.load(config)
                params_config = api_config['params']
        curr_api_description = _to_html(element['description'])
    context = {'user': user,
               'api_list': api_list,
               'curr_api_uri': curr_api_uri,
               'curr_api_path': 'http://' + request.environ['HTTP_HOST'] + (curr_api_uri or ''),
               'curr_api_method': method_name,
               'curr_api_params': element['param_list'],
               'curr_api_codes': curr_api_codes,
               'api_config': api_config,
               'params_config': params_config,
               'curr_api_description': curr_api_description,
               'post_type': post_type,
               'json_p': json_p}

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
