import json
from flask import request, render_template, Response, current_app as app
from fair import JSON, CView



def save_case():
    result = app.config['test_ui'].save_case(**request.json)
    return Response(json.dumps(result), content_type=JSON)


def save_config():
    result = app.config['test_ui'].save_config(**request.json)
    return Response(json.dumps(result), content_type=JSON)





