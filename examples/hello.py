from fair import Fair

app = Fair(__name__)


@app.route('/hello', methods='get')
def get(uid):
    """ Hello Fair-API

    :plugin: json_p
    :param Int * uid: you id ...
    """
    return 'Hello %s' % uid


@app.route('/hello', methods='post')
def post(name):
    """ Hello Fair-API

    :param Str * name: you name ...
    """
    return 'Hello %s' % name


@app.route('/echo', methods='post')
def echo(name):
    """ Hello Fair-API

    :param Str * name: you name ...
    """
    return 'Echo %s' % name


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
#         'test_ui': {
#             'uri': 'tests'
#         }
#     }
#     app.config['web_ui'] = web_ui_config
#     setup_web_ui(app, web_ui_config, cache_path, TestsLocalStorage)
