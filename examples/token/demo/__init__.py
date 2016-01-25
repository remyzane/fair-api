# -*- coding: utf-8 -*-

import os
import json
import logging
from flask import Flask
from http_api.utility import load_yaml, set_logging
from http_api.configure import http_api_setup

from .utility import program_dir

log = logging.getLogger(__name__)

# load config file
config = load_yaml(os.path.join(program_dir, 'demo.yml'))

app = application = http_api_setup(config)

