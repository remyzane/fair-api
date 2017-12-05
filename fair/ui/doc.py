from flask import Flask, request, render_template

from ..utility import ContextClass, request_args, rst_to_html, text_to_html
from ..element import Element


def fair_ui(element, sign='test'):
    # if sign == 'doc':
    response_doc = None
    if element.response:
        response_doc = rst_to_html(element.response.__doc__)
    return render_template('doc.html',
                           title='DOC UI',
                           api_uri='/',
                           method=request.method,
                           element=element,
                           api_title=text_to_html(element.title),
                           response_doc=response_doc,
                           description=text_to_html(element.description))
