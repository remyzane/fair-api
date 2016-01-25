# -*- coding: utf-8 -*-

import os
import json
from flask import request
from http_api.plugin.jsonp import JsonP

# from demo.utility import program_dir

def _params_not_equal(old_params, new_params):
    for param in old_params:
        if old_params[param] != new_params.get(param):
            return True
    for param in new_params:
        if new_params[param] != old_params.get(param):
            return True
    return False


class TestsUI(object):

    def __init__(self, workspace, params=None):
        pass

    def get_case(self):
        pass

    def set_case(self, user, uri, method, param_mode, params, code):
        result = []
        case_path = os.path.join(get_case_dir(user, uri, method), code)
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
        return {'result': 'success'}


    def set_config(self):
        pass


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


def get_curr_api_params(param_list, config):
    params = []
    params_config = config['params'] if config else {}
    for param in param_list:
        name = param['name']
        requisite = '●' if param['requisite'] else ''
        if param['type'].has_sub_type:
            type_name = '%s[%s]' % (param['type'].__name__, param['type'].type.__name__)
            type_display = '''<span message="%s">%s</span>[<span message="%s">%s</span>]''' % (
                param['type'].description, param['type'].__name__,
                param['type'].type.description, param['type'].type.__name__)
        else:
            type_name = param['type'].__name__
            type_display = '''<span class="show-message" message="%s">%s</span>''' % \
                           (to_html(param['type'].description), param['type'].__name__)
        pure_auto = 'checked="checked"' if name in params_config and params_config[name]['pure_auto'] else ''
        param_url = params_config[name]['url'] if name in params_config else ''
        params.append((name, requisite, to_html(param['description']), type_name, type_display, pure_auto, param_url))
    return params


# get detail info of current api
def get_curr_api(user, view, method):
    context = dict()
    api_config_path = os.path.join(get_case_dir(user, view.uri, method.__name__.upper()), '__config__')
    if os.path.exists(api_config_path):
        with open(api_config_path, 'r') as config:
            context['curr_api_config'] = json.load(config)

    title, description = method.element.title, method.element.description
    context['curr_api_uri'] = view.uri
    context['curr_api_path'] = 'http://' + request.environ['HTTP_HOST'] + view.uri
    context['curr_api_method'] = method.__name__.upper()
    context['curr_api_params'] = get_curr_api_params(method.element.param_list, context.get('curr_api_config'))
    context['curr_api_description'] = to_html(title + (os.linesep*2 if description else '') + description)
    context['curr_api_json_p'] = None
    context['curr_api_config'] = {}
    context['curr_api_params_config'] = {}
    context['curr_api_codes'] = get_sorted_code(user, view, method)

    for plugin in method.element.plugins:
        if isinstance(plugin, JsonP):
            context['curr_api_json_p'] = plugin.callback_field_name
    return context
