from flask import Flask, request, render_template

from .ui import doc, setup as setup_ui
from . import register
from .utility import ContextClass, request_args, rst_to_html, text_to_html
from .element import Element


def set_view_func(fair_conf, view_func, rule):
    """
    :param fair_conf:
    :param view_func:
    :param rule:
    :return:
    """
    # get element info from fn doc
    element = Element(fair_conf, view_func, rule)

    fn_fair = ContextClass(element=element)

    for plugin in element.plugins:
        plugin.init_view(fn_fair)
        # add plugin.parameters to method.element.param_list.
        if plugin.parameters:
            plugin_parameters = list(plugin.parameters)
            param_list = list(element.param_list)
            while plugin_parameters:
                p = plugin_parameters.pop()
                param_list.insert(0, {'name': p[0], 'type': p[1], 'requisite': p[2], 'description': p[3]})
            element.param_list = tuple(param_list)

    view_func.__fair__ = fn_fair


class Fair(Flask):
    """ """

    def __init__(self, import_name, **kwargs):
        super(Fair, self).__init__(import_name, **kwargs)
        setup_ui(self)
        self.config['fair'] = register.default()

    def route(self, url=None, **options):

        def decorator(view_func):
            endpoint = options.pop('endpoint', url)
            self.add_url_rule(url, endpoint, view_func, **options)
            rule = self.url_map._rules_by_endpoint[endpoint][0]
            print(dir(rule))
            set_view_func(self.config['fair'], view_func, rule)

            return view_func

        return decorator

    def preprocess_request(self):
        view_func = self.view_functions[request.endpoint]

        return super(Fair, self).preprocess_request()

    def dispatch_request(self):
        view_func = self.view_functions[request.endpoint]
        response_accept = request.headers.get('Accept')

        element = getattr(view_func.__fair__, 'element')  # type: Element
        if 'text/html' in response_accept:
            sign = request_args('__fair')
            # if sign:
            return doc.fair_ui(element, sign)

        response = super(Fair, self).dispatch_request()
        return response