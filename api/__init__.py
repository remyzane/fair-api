# -*- coding: utf-8 -*-

import logging
from flask import Flask, session, request, render_template, Response     # for the convenience of import

from .api import Api, RR, JSON, JSON_P
from .parameter import *

log = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../www', static_url_path='/res',  template_folder='../')


# cannot import view and model before call this function
def init(config):
    from .configure import set_database, set_flask, set_view
    # configure database (execution of this config must preceded view and model import)
    set_database(config['databases'])
    # configure flask
    set_flask(app, config['app'])
    # configure view
    set_view(app, config['view_packages'])


# TODO add customize_token demo
# TODO DOC
# TODO auto unit test for user case
# TODO translate zh -> en
