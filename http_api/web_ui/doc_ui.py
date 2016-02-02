from flask import request, render_template, current_app as app
from http_api import JSON, CView

from .test_ui import to_html


def index():
    api_list = []
    view_keys = list(app.view_functions.keys())
    view_keys.sort()
    for name in view_keys:
        view_class = getattr(app.view_functions[name], 'view_class', None)
        if view_class and issubclass(view_class, CView) and view_class != CView:
            methods = list(view_class.request_methods.keys())
            methods.sort()
            for method_name in methods:
                method = view_class.request_methods[method_name]
                api_list.append((view_class.uri,
                                 method_name,
                                 method.element,
                                 to_html(method.element.title),
                                 to_html(method.element.description),
                                 ))
    title = app.config['web_ui']['doc_ui'].get('title', 'DOC UI')
    return render_template('doc_ui.html', api_list=api_list, title=title)
