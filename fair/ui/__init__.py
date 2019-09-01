from flask import Response
from ..response import ResponseRaise
from ..utility import get_request_params, text_to_html, rst_to_html

from fair.utility import ContextClass


def match(app, request):
    """ Check fair ui whether or not shown

    keep it simple for performance
    """
    if request.path in app.api.url_map:
        for view_func, methods in app.api.url_map[request.path].items():
            if request.method in methods:
                if app.api:
                    return True
    return False


def structure_params(view_func, params_proto, params):

    # check the necessary parameter's value is sed
    for param in view_func.meta.param_not_null:
        if params_proto.get(param, '') == '':       # 0 is ok
            raise view_func.meta.response('param_missing', {'parameter': param})

    ret = view_func.meta.param_default.copy()
    # parameter's type of proof and conversion
    for param, value in params.items():
        if param not in view_func.meta.param_index:
            raise view_func.meta.response('param_unknown', {'parameter': param, 'value': value})
        if value is not None:
            try:
                ret[param] = view_func.meta.param_types[param].structure(view_func, value)
            except Exception as e:
                raise view_func.meta.response(view_func.meta.param_types[param].error_code, {'parameter': param, 'value': value})
    return ret


def adapter(app, request):
    view_func = None
    views = app.api.url_map.get(request.path)

    for view, support_methods in views.items():
        if request.method in support_methods:
            view_func = view
            break

    if not hasattr(view_func, 'meta'):
        return Response('406 Current url not have Fair UI', status=406)

    try:
        # get request parameters
        params = get_request_params(request)
        params_proto = params.copy()

        # plugin
        for plugin in view_func.meta.plugins:
            plugin.before_request(view_func)
            for parameter in plugin.parameters:
                del params[parameter[0]]

        # structure parameters
        params = structure_params(view_func, params_proto, params)
        request.meta = view_func.meta
        response_content = view_func(**params)
        if isinstance(response_content, ResponseRaise):
            response_content = response_content.response()
    except ResponseRaise as response_raise:
        response_content = response_raise.response()
    except Exception as e:
        response_content = view_func.meta.response('exception').response()
    return response_content


def get_view_context(views):

    context = ContextClass()


    if len(views) == 1:
        view_func = tuple(views)[0]
        http_methods = views[view_func]
    else:
        method = request.args.get('method', None)
        if method:
            method = method.upper()
            for view_func, http_methods in views.items():
                if method in http_methods:
                    pass