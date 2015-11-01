# -*- coding: utf-8 -*-

import logging
from flask import Flask, session, request, render_template, Response     # 方便项目引用

from .api import Api, RR, JSON, JSON_P
from .parameter import *

log = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../www', static_url_path='/res',  template_folder='../')


# 本函数调用前请勿导入view和model, Api类中声明了db['default'](本函数调用前不存在)
def init(config):
    from .configure import set_database, set_flask, set_view
    # 设置数据库(必须先于view和model导入之前调用)
    set_database(config['databases'])
    # 设置flask
    set_flask(app, config['app'])
    # 设置视图
    set_view(app, config['view_packages'])


# TODO check chinese comments  then translate
# TODO DOC
# TODO The web test case's automation (in unit test)
