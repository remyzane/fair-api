import os
import json
from flask import request
from fair.plugin.jsonp import JsonP
from fair.utility import text_to_html


class CaseStorage(object):

    def get_case(self, view, method):
        raise NotImplementedError

    def save_case(self, api_path, method, param_mode, params, code):
        raise NotImplementedError

    def save_config(self, api_path, method, post_type, json_p, params):
        raise NotImplementedError

    @staticmethod
    def params_not_equal(old_params, new_params):
        for param in old_params:
            if old_params[param] != new_params.get(param):
                return True
        for param in new_params:
            if new_params[param] != old_params.get(param):
                return True
        return False


class CaseLocalStorage(CaseStorage):

    def __init__(self, workspace):
        self.workspace = workspace

    def get_case(self, view, method):
        context = {'api_config': {}, 'api_json_p': None}
        api_config_path = os.path.join(self.get_case_dir(view.uri, method.__name__.upper()), '__config__')
        if os.path.exists(api_config_path):
            with open(api_config_path, 'r') as config:
                context['api_config'] = json.load(config)

        # title, description = method.meta.title, method.meta.description
        # context['api_uri'] = view.uri
        # context['api_path'] = 'http://' + request.environ['HTTP_HOST'] + view.uri
        # context['api_method'] = method.__name__.upper()
        # context['api_params'] = get_api_params(method.meta.param_list, context.get('api_config'))
        # context['api_description'] = text_to_html(title + (os.linesep*2 if description else '') + description)
        # context['api_params_config'] = {}
        context['api_codes'] = self.get_sorted_code(view, method)

        for plugin in method.api.plugins:
            if isinstance(plugin, JsonP):
                context['api_json_p'] = plugin.callback_field_name
        return context

    def get_exe_case(self, view, method, code):
        use_cases = ''
        case_path = os.path.join(self.get_case_dir(view.uri, method.__name__.upper()), code)
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


    def get_case_dir(self, api_uri, method_name):
        api_path = '_'.join(api_uri[1:].split('/'))
        case_dir = os.path.realpath(os.path.join(self.workspace, 'exe_ui', api_path, method_name))
        if not os.path.exists(case_dir):
            os.makedirs(case_dir)
        return case_dir

    def save_case(self, api_path, method, param_mode, params, code):
        result = []
        case_path = os.path.join(self.get_case_dir(api_path, method), code)
        new_data = json.dumps({
            'param_mode': param_mode,
            'params': params
        }) + os.linesep
        # read old record
        if os.path.exists(case_path):
            data_file = open(case_path, 'r')
            for line in data_file.readlines():
                line_data = json.loads(line)
                if line_data['param_mode'] != param_mode or self.params_not_equal(line_data['params'], params):
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

    def save_config(self, api_path, method, post_type, json_p, params):
        config_path = os.path.join(self.get_case_dir(api_path, method), '__config__')
        # save configure
        data_file = open(config_path, 'w')
        data_file.write(json.dumps({'method': method, 'post_type': post_type, 'json_p': json_p, 'params': params}))
        data_file.close()
        return {'result': 'success'}

    def get_sorted_code(self, view, method):
        codes = []
        is_param_type = False
        for error_code in method.api.code_index:
            error_message = method.api.code_dict[error_code]

            if error_code.startswith('param_type_error_') and not is_param_type:
                codes.append(('----', None, None))
                is_param_type = True

            if is_param_type and not error_code.startswith('param_type_error_'):
                codes.append(('----', None, None))
                is_param_type = False

            codes.append((error_code, text_to_html(error_message),
                          self.get_exe_case(view, method, error_code)))

        return codes
