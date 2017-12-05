from flask import request, render_template, current_app as app
from werkzeug.routing import Rule

from ..element import Element


def test_ui(view_func):
    rule = view_func.rule           # type: Rule
    element = view_func.element     # type: Element
    curr_api_context = {}
    user = request.args.get('user', '')
    # context = {'user': user,
    #            'title': 'Test UI',
    #            'web_ui_uri': app.config['web_ui']['uri'],
    #            'test_ui_uri': app.config['web_ui']['test_ui']['uri'],
    #            'post_type': request.args.get('type', 'j')}

    # for name in app.view_functions.keys():
    #     view_class = getattr(app.view_functions[name], 'view_class', None)
    #     if view_class and issubclass(view_class, CView) and view_class != CView:
    #         for method_name in view_class.request_methods.keys():
    #             method = view_class.request_methods[method_name]
    #             if view_class.uri == request.args.get('api', '') and method_name == request.args.get('method', ''):
    #                 curr_api_context = app.config['test_ui'].get_case(user, view_class, method)
    # context.update(curr_api_context)
    return render_template('test.html',
                           url=request.path,
                           methods=rule.methods,
                           curr_api_config={}
                           )