# -*- coding: utf-8 -*-

import os
import json
import logging
from flask import Flask
from curd.utility import load_yaml, set_logging
from curd.configure import curd_setup

from .utility import program_dir

log = logging.getLogger(__name__)

# load config file
config = load_yaml(os.path.join(program_dir, 'demo.yml'))

# setting logging
set_logging(config['logging'], os.path.join(program_dir, 'work'))
# log.debug('app config: %s', json.dumps(config['app'], indent=4))

# create application
app = application = Flask(__name__, static_folder='../www', static_url_path='/res',  template_folder='../')
curd_setup(app, config)


# TODO check chinese comments  then translate
# TODO DOC
# TODO The web test case's automation (in unit test)
