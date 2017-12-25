from flask import Response

from fair.utility import ContextClass


def match(app, request):
    """ Check fair ui whether or not shown

    keep it simple for performance
    """

    if request.method == 'GET' and request.path in app.air.url_map:

        if 'fair' in request.args:
            return True

        if app.air.browsable:
            response_accept = request.headers.get('Accept')
            if 'text/html' in response_accept:
                return True

    return False


def adapter(app, request):
    from .doc import doc_ui
    from .test import test_ui

    sign = request.args.get('fair', 'test')

    method = request.args.get('method', None)

    views = app.air.url_map.get(request.path)


    return Response('404 NOT FOUND', status=404)

    if not hasattr(view_func, 'element'):
        return Response('406 Current url not have Fair UI', status=406)

    if sign == 'doc':
        return doc_ui(view_func)

    if sign == 'test':
        return test_ui(view_func)

    return Response('406 Fair not support [%s]' % sign, status=406)


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