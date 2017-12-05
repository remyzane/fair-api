import os
from flask import Blueprint


def setup(app):
    templates_path = os.path.realpath(os.path.join(__file__, '..', 'templates'))
    fair_ui = Blueprint('__fair__', __name__, template_folder=templates_path)
    app.register_blueprint(fair_ui)
