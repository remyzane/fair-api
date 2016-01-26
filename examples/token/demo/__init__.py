# -*- coding: utf-8 -*-

from flask import Flask
from http_api.configure import http_api_setup

from .utility import program_dir, get_config

# load config
config = get_config(program_dir, 'demo.yml')

# create wsgi application
app = application = Flask(__name__)

workspace = http_api_setup(app, config)
