from flask import request, render_template
from werkzeug.routing import Rule

from ..utility import rst_to_html, text_to_html
from ..api_meta import Meta


def doc_ui():

    return 'aaa'
    meta = view_func.meta     # type: Meta
    response_doc = None
    if element.response:
        response_doc = rst_to_html(element.response.__doc__)
    return render_template('doc.html',
                           url=request.path,
                           # methods=method_filter(view_func.element),
                           methods=element.http_methods,
                           element=element,
                           title=text_to_html(element.title),
                           response_doc=response_doc,
                           description=text_to_html(element.description))
