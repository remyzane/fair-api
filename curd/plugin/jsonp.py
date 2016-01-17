# -*- coding: utf-8 -*-

from curd.view import CView
from curd.plugin import Plugin


class JsonP(Plugin):
    """API Plugin parent class.

    :cvar dict codes: error code and message
    """
    error_codes = {}

    @classmethod
    def reconstruct(cls, params):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param dict params: plug config parameters
        """

    # @classmethod
    # def __check(cls, method):
    #     # POST method not support jsonp
    #     elif hasattr(cls, 'post'):
    #         if cls.json_p:
    #             raise Exception('Error define in %s: POST method not support jsonp.' % cls.__name__)

        pass

    @classmethod
    def init_view(cls, view_class, method):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view_class: view class
        """
        if method.__name__ is not 'get':
            raise Exception('Error define in %s.%s: json_p plugin only support GET method.' %
                            (view_class.__name__, method.__name__))

    @classmethod
    def before_request(cls, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
                        # if self.json_p:
                #     # jquery's cache management mechanism will add '_', '1_' parameter,
                #     # let jquery don't add '_' parameter's method: set 'cache: true' in jquery's ajax method
                #     if param == self.json_p or param == '_' or param == '1_':
                #         continue

        pass

    @classmethod
    def after_request(cls, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
        pass
