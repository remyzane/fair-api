# -*- coding: utf-8 -*-

import os
from flask import Blueprint

from .test_view import index as tests_index, save_case


def setup_web_ui(app, config, workspace, log_ui_class, test_ui_class):
    static_path = os.path.realpath(os.path.join(__file__, '..', 'static'))
    web_ui = Blueprint('web_ui', __name__,
                       template_folder='templates',
                       static_url_path='/%s/static' % config['uri'],
                       static_folder=static_path)

    web_ui.add_url_rule('/%s/tests/' % config['uri'], 'tests', tests_index)
    web_ui.add_url_rule('/%s/tests/save_case' % config['uri'], 'tests_save_case', save_case, methods=['POST'])
    web_ui.add_url_rule('/%s/tests/save_config' % config['uri'], 'tests_save_config', save_case, methods=['POST'])
    app.register_blueprint(web_ui)
    app.config['log_ui'] = log_ui_class(workspace, config.get('log_ui'))
    app.config['test_ui'] = test_ui_class(workspace, config.get('test_ui'))
