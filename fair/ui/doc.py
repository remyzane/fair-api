from flask import request, render_template
from werkzeug.routing import Rule

from . import method_filter
from ..utility import rst_to_html, text_to_html
from ..element import Element


def doc_ui(view_func):
    rule = view_func.rule           # type: Rule
    element = view_func.element     # type: Element
    response_doc = None
    if element.response:
        response_doc = rst_to_html(element.response.__doc__)
    return render_template('doc.html',
                           url=request.path,
                           methods=method_filter(view_func.element),
                           element=element,
                           title=text_to_html(element.title),
                           response_doc=response_doc,
                           description=text_to_html(element.description))