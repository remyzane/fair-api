from fair import Fair
from flask import request
from fair.response import JsonRaise

app = Fair(__name__)


@app.route('/hello', methods='get')
def get(uid):
    """ Hello Fair-API

    :plugin: json_p
    :param Int * uid: you id ...
    """
    return JsonRaise('success', {'uid': uid})


@app.route('/hello', methods=['put', 'post'])
def post(name, msg):
    """ Hello Fair-API

    :param Str * name: you name ...
    :param Str msg: you message ...
    """
    return JsonRaise('success', {'name': name, 'msg': msg})


@app.route('/echo', methods='post')
def echo(name):
    """ Hello Fair-API

    :param Str * name: you name ...
    """
    return JsonRaise('success', {'name': name})


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)


#
#
# def setup(app, cache_path,
#                responses=None,
#                plugins=None,
#                parameter_types=None):
#
#
#
#     app.config['responses'] = {'default': JsonRaise}
#
#     # set parameter types
#     set_parameter_types(app, parameter_types)
#
#     # configure web ui
#     web_ui_config = {
#         'uri': 'api',
#         'exe_ui': {
#             'uri': 'tests'
#         }
#     }
#     app.config['web_ui'] = web_ui_config
#     setup_web_ui(app, web_ui_config, cache_path, CaseLocalStorage)
