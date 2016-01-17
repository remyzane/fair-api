# -*- coding: utf-8 -*-

from curd.view import CView
from curd.plugin import Plugin


class JsonP(Plugin):
    """API Plugin parent class.

    :cvar dict codes: error code and message
    """
    error_codes = {}

    def __init__(self, params):
        """Plugin init

        :param dict params: plug config parameters
        """
        self.callback_field_name = params['callback_field_name']

    def init_view(self, view_class, method):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view_class: view class
        """
        if method.__name__ is not 'get':
            raise Exception('Error define in %s.%s: json_p plugin only support GET method.' %
                            (view_class.__name__, method.__name__))

    def before_request(self, view, method):
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
