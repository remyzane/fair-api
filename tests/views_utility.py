# -*- coding: utf-8 -*-


import os
import json
from flask import request
from curd.plugin.jsonp import JsonP

from demo.utility import program_dir


def to_html(text):
    text = text.replace('&', '&#38;')
    text = text.replace(' ', '&nbsp;')
    text = text.replace(' ', '&#160;')
    # text = text.replace('<', '&#60;')
    # text = text.replace('>', '&#62;')
    text = text.replace('"', '&#34;')
    text = text.replace('\'', '&#39;')
    text = text.replace(os.linesep, '</br>')
    return text


def get_case_dir(user, curr_api_uri, method_name):
    api_path = '_'.join(curr_api_uri[1:].split('/'))
    case_dir = os.path.realpath(os.path.join(program_dir, 'work', 'test', 'case', user, api_path, method_name))
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    return case_dir


def get_sorted_code(user, view, method):
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

        codes.append((error_code, to_html(error_message),
                      get_test_case(user, view, method, error_code)))

    return codes


def get_test_case(user, view, method, code):
    use_cases = ''
    case_path = os.path.join(get_case_dir(user, view.uri, method.__name__.upper()), code)
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


def get_curr_api_params(param_list):
    params = []
    for param in param_list:
        requisite = '●' if param['requisite'] else ''
        print(param)
        if param['type'].has_sub_type:
            type_name = '%s[%s]' % (param['type'].__name__, param['type'].type.__name__)
            type_display = '''<span title="%s">%s</span>[<span title="%s">%s</span>]''' % (
                param['type'].description, param['type'].__name__,
                param['type'].type.description, param['type'].type.__name__)
        else:
            type_name = param['type'].__name__
            type_display = '''<span title="%s">%s</span>''' % (param['type'].description, param['type'].__name__)
        params.append((param['name'], requisite, param['description'], type_name, type_display))
    return params


# get detail info of current api
def get_curr_api(user, view, method):
    context = dict()
    context['curr_api_uri'] = view.uri
    context['curr_api_path'] = 'http://' + request.environ['HTTP_HOST'] + view.uri
    context['curr_api_method'] = method.__name__.upper()
    context['curr_api_params'] = get_curr_api_params(method.element.param_list)
    context['curr_api_description'] = to_html(method.element.description)
    context['curr_api_json_p'] = None
    context['curr_api_config'] = {}
    context['curr_api_params_config'] = {}
    context['curr_api_codes'] = get_sorted_code(user, view, method)
    api_config_path = os.path.join(get_case_dir(user, view.uri, method.__name__.upper()), '__config__')
    if os.path.exists(api_config_path):
        with open(api_config_path, 'r') as config:
            context['curr_api_config'] = json.load(config)
            context['curr_api_params_config'] = context['curr_api_config']['params']
    for plugin in method.element.plugins:
        if isinstance(plugin, JsonP):
            context['curr_api_json_p'] = plugin.callback_field_name
    print(context['curr_api_params'])
    print(context['curr_api_params_config'])
    return context
