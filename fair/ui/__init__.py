from flask import Response


def method_filter(methods):
    ret = []
    for method in methods:
        if method not in ('OPTIONS', 'HEAD'):
            ret.append(method)
    ret.sort()
    return set(ret)


def adapter(view_func, sign='test'):
    from .doc import doc_ui
    from .test import test_ui

    if not view_func:
        return Response('404 NOT FOUND', status=404)
    if not hasattr(view_func, 'rule') or not hasattr(view_func, 'element'):
        return Response('406 Current url not have Fair UI', status=406)

    if sign == 'doc':
        return doc_ui(view_func)

    if sign == 'test':
        return test_ui(view_func)

    return Response('406 Fair not support [%s]' % sign, status=406)
