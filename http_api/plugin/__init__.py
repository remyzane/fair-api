# -*- coding: utf-8 -*-

from http_api.view import CView


class Plugin(object):
    """API Plugin parent class.

    :cvar dict codes: error code and message
    """
    codes = {}

    def __init__(self, params):
        """Plugin init

        :param dict params: plug config parameters
        """

    def init_view(self, view_class, method):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view_class: view class
        """

    def before_request(self, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """

    def after_request(self, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
