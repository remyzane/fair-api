# -*- coding: utf-8 -*-

import os
from flask import Flask
from http_api.utility import load_yaml
from http_api.configure import http_api_setup

from .utility import program_dir

# load config file
config = load_yaml(os.path.join(program_dir, 'demo.yml'))

# create wsgi application
app = application = Flask(__name__, static_folder='../www', static_url_path='/res',  template_folder='../')

http_api_setup(app, config)
