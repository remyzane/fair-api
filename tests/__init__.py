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
    text = text.replace('<', '&#60;')
    text = text.replace('>', '&#62;')
    text = text.replace('"', '&#34;')
    text = text.replace('\'', '&#39;')
    text = text.replace(os.linesep, '</br>')
    return text


def _get_case_dir(curr_api_uri, user):
    api_path = '_'.join(curr_api_uri[1:].split('/'))
    case_dir = os.path.realpath(os.path.join(program_dir, 'work', 'test', 'case', user, api_path))
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    return case_dir


def _get_sorted_code(curr_api_cls, user, curr_api_uri):
    codes = []
    c_keys = list(curr_api_cls.codes)
    # common
    keys = ['success', 'exception', 'param_unknown']
    c_keys.remove('success')
    c_keys.remove('exception')
    c_keys.remove('param_unknown')
    if curr_api_cls.requisite:
        c_keys.remove('param_missing')
        keys.append('param_missing')
    # type matching
    type_keys = []
    for name in dir(parameter):
        cls = getattr(parameter, name)
        if hasattr(cls, 'code') and hasattr(cls, 'message') and getattr(cls, 'code') != '':
            code = getattr(cls, 'code')
            if code in c_keys:
                c_keys.remove(code)
                type_keys.append(code)
    for _name in dir(plugin):
        if _name[:2] != '__':
            obj = getattr(plugin, _name)
            if type(obj) == type(object) and issubclass(obj, plugin.Plugin) and obj is not plugin.Plugin:
                for code in obj.codes:
                    if code in c_keys:
                        c_keys.remove(code)
                        type_keys.append(code)
    if type_keys:
        keys.append('----')
        keys = keys + type_keys
    # custom errors
    if c_keys:
        c_keys.sort()
        keys.append('----')
        keys = keys + c_keys
    for key in keys:
        if key == '----':
            codes.append(('----', None, None))
        else:
            codes.append((key, _to_html(curr_api_cls.codes[key]), _get_test_case(curr_api_uri, user, key)))
    return codes


def _get_test_case(curr_api_uri, user, code):
    use_cases = ''
    case_path = os.path.join(_get_case_dir(curr_api_uri, user), code)
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
    curr_api_cls = None
    curr_api_uri = None
    curr_api_method = None
    curr_api_params = []
    curr_api_codes = []
    api_config = {}
    params_config = {}
    curr_api_description = None
    param_curr_uri = request.args.get('api', '')
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
                            uri = '/%s/%s' % (package_name, name)
                            api_list.append((uri, _to_html(view.description)))
                            if uri == param_curr_uri:
                                curr_api_uri = uri
                                curr_api_cls = view
                    except TypeError:
                        pass
    # get detail info of current api
    json_p = ''
    if curr_api_cls:
        json_p = curr_api_cls.json_p
        curr_api_method = 'GET' if hasattr(curr_api_cls, 'get') else 'POST'
        parameters, requisite = curr_api_cls.parameters, curr_api_cls.requisite
        for param in requisite:
            param_type = parameters.get(param)
            curr_api_params.append((param, param_type.__name__ if param_type else 'Str', True))
        param_keys = list(parameters.keys())
        param_keys.sort()
        for param in param_keys:
            if param not in requisite:
                param_type = parameters.get(param)
                curr_api_params.append((param, param_type.__name__ if param_type else 'Str', False))
        curr_api_codes = _get_sorted_code(curr_api_cls, user, curr_api_uri)
        api_config_path = os.path.join(_get_case_dir(curr_api_uri, user), '__config__')
        if os.path.exists(api_config_path):
            with open(api_config_path, 'r') as config:
                api_config = json.load(config)
                params_config = api_config['params']
        curr_api_description = _to_html(curr_api_cls.description)
    context = {'user': user,
               'api_list': api_list,
               'curr_api_uri': curr_api_uri,
               'curr_api_path': 'http://' + request.environ['HTTP_HOST'] + (curr_api_uri or ''),
               'curr_api_method': curr_api_method,
               'curr_api_params': curr_api_params,
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
    code = request.json['code']

    result = []
    case_path = os.path.join(_get_case_dir(request.json['api_path'], user), code)
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
    config_path = os.path.join(_get_case_dir(request.json['api_path'], user), '__config__')

    data = request.json.copy()
    del data['user']
    del data['api_path']

    # save configure
    data_file = open(config_path, 'w')
    data_file.write(json.dumps(data))
    data_file.close()

    return Response(json.dumps({'result': 'success'}), content_type=JSON)
