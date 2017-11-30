from flask import Response, current_app
from .configure import setup


from .view import CView
from .response import JSON, JSON_P, ResponseRaise, JsonRaise
from .parameter import *
from .plugin import Plugin
from .element import Element

class ContextClass(object):
    """ Context Class
    ab = ContextClass(a=1, b=2)      ab.__dict__  # {'a': 1, 'b': 2}
    """
    def __init__(self, **params):
        for key, value in params.items():
            setattr(self, key, value)


# def route():
#     def decorator(fn):
#         element = Element(fn)
#
#         fn_fair = ContextClass(element=element)
#         fn.__fair__ = fn_fair
#         return fn
#
#     return decorator
#


def route(rule, **options):
    """ view action 装饰器
    用于判定访问权限等
    renderer: json、jsonp
    """

    def decorator(fn):

        def wraped(*args, **kwargs):
            return fn()

        endpoint = options.pop('endpoint', None)
        current_app.add_url_rule(rule, endpoint, wraped, **options)
        return wraped

    return decorator
