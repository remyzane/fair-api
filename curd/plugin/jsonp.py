# -*- coding: utf-8 -*-

from curd.view import CView
from curd.plugin import Plugin
from flask import current_app as app


class JsonP(Plugin):
    """API Plugin parent class.

    if defined in view's return will using jsonp (accustomed to using 'callback')

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

    def before_request(self, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
        if self.callback_field_name in view.params:
            view.json_p_callback_name = view.params[self.callback_field_name]
            view.raise_response = app.config['responses']['json_p']
            del view.params[self.callback_field_name]
            if '_' in view.params:
                del view.params['_']
            if '1_' in view.params:
                del view.params['1_']
