#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import logging
from importlib import import_module

# setting logging
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel('DEBUG')

# set path for fair-api
sys.path.insert(0, 'fair-api')
sys.path.insert(0, 'example')

# get example
example_name = sys.argv[1]
example = import_module(example_name)

# run example
example.app.debug = True
example.app.jinja_env.auto_reload = True
example.app.run('0.0.0.0', 5000, use_reloader=True)
