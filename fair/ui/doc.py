from flask import request, render_template
from werkzeug.routing import Rule

from ..utility import rst_to_html, text_to_html, ContextClass
from ..api_meta import Meta
from flask import current_app as app


def doc_ui():
    views = app.api.url_map[request.url_rule.rule[:-5]]
    apis = []
    for view_func in views:
        meta = view_func.meta       # type: Meta
        response_doc = None
        if meta.response:
            response_doc = rst_to_html(meta.response.__doc__)
        apis.append(ContextClass(title=text_to_html(meta.title), description=text_to_html(meta.description),
                                 methods=meta.http_methods, meta=meta, response_doc=response_doc))
    return render_template('doc.html', apis=apis)    # url 为 flask 模板内置变量
