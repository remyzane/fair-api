import os
import logging
from flask import Blueprint

from .doc_ui import index as doc_index
from .test_view import index as test_index, save_case, save_config

log = logging.getLogger(__name__)


def setup_web_ui(app, config, workspace, log_ui_class, test_ui_class):
    web_uri = config['uri']
    doc_uri = config['doc_ui']['uri']
    test_uri = config['test_ui']['uri']
    static_path = os.path.realpath(os.path.join(__file__, '..', 'static'))
    templates_path = os.path.realpath(os.path.join(__file__, '..', 'templates'))
    log.debug('templates_path: %s', templates_path)
    web_ui = Blueprint('web_ui', __name__,
                       template_folder=templates_path,
                       static_url_path='/%s/static' % web_uri,
                       static_folder=static_path)
    web_ui.add_url_rule('/%s/%s/' % (web_uri, doc_uri), doc_uri, doc_index)
    web_ui.add_url_rule('/%s/%s/' % (web_uri, test_uri), test_uri, test_index)
    web_ui.add_url_rule('/%s/%s/save_case' % (web_uri, test_uri), test_uri + '_save_case', save_case, methods=['POST'])
    web_ui.add_url_rule('/%s/%s/save_config' % (web_uri, test_uri), test_uri + '_save_config',
                        save_config, methods=['POST'])
    app.register_blueprint(web_ui)
    app.config['log_ui'] = log_ui_class(workspace, config.get('log_ui'))
    app.config['test_ui'] = test_ui_class(workspace, config.get('test_ui'))
