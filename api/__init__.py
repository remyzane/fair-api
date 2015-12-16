# -*- coding: utf-8 -*-

import os
import logging
from flask import Flask, session, request, render_template, Response     # for the convenience of import

from .api import Api, RR, JSON, JSON_P
from .parameter import *
from .utility import load_yaml, program_dir, set_logging
from .configure import set_database, set_flask, set_view

log = logging.getLogger(__name__)

# load config file
work_dir = os.path.join(program_dir, 'work')
config = load_yaml(os.path.join(work_dir, 'api.yml'))

# setting logging
set_logging(config['logging'], work_dir)

# create application
app = application = Flask(__name__, static_folder='../www', static_url_path='/res',  template_folder='../')

# configure database (cannot import view and model before call this function)
set_database(config['databases'])
# configure flask
set_flask(app, config['app'])
    # configure view
set_view(app, config['view_packages'])


# TODO check chinese comments  then translate
# TODO DOC
# TODO The web test case's automation (in unit test)
