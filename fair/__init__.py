from .configure import setup
from .view_old import CView
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
