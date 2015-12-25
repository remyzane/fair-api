# -*- coding: utf-8 -*-

from curd.view import CView
from curd.plugin import Plugin


class JsonP(Plugin):
    """API Plugin parent class.

    :cvar dict codes: error code and message
    """
    codes = {}

    @classmethod
    def reconstruct(cls, params):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param dict params: plug config parameters
        """
        pass

    @classmethod
    def init_view(cls, view_class):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view_class: view class
        """
        pass

    @classmethod
    def before_request(cls, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
        pass

    @classmethod
    def after_request(cls, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
        pass
