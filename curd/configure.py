# -*- coding: utf-8 -*-

import peewee
import logging
import pkgutil
import datetime

from .utility import class_name_to_api_name

log = logging.getLogger(__name__)

db_classes = {
    'mysql': peewee.MySQLDatabase,
    'pgsql': peewee.PostgresqlDatabase,
    'sqlite': peewee.SqliteDatabase
}
db = {}


# configure database (execution of this config must preceded view and model import)
def set_database(config):
    """Configure database.

     cannot import view and model before call this function

    :param config: database's config
    :type  config: dict
    """
    global db
    for database in config:
        db[database['key']] = db_classes[database['type']](**config[0]['params'])
    # set default db
    peewee.Model._meta.database = db.get('default') or db[0]


# configure flask (app.config) defined in app section at project.yml
def set_app(app, config):
    """Configure flask app.

    :param app: Flask app object
    :param config: api's config
    :type  config: dict
    """
    # app config
    for name in config['app']:
        app.config[name] = config['app'][name]
    # flask config
    for name in config['flask']:
        # set the expiration date of a permanent session.
        if name == 'PERMANENT_SESSION_LIFETIME':
            app.config[name] = datetime.timedelta(days=int(config['flask'][name]))
        else:
            app.config[name] = config['flask'][name]


# 设置view
def set_view(app, config):
    """Configure view

    url route configure.

    :param app: Flask app object
    :param config: view's config
    :type  config: dict
    """
    from .view import CView
    app.view_packages = config
    for package_name in app.view_packages:
        exec('import %s as package' % package_name)
        for importer, modname, is_pkg in pkgutil.iter_modules(locals()['package'].__path__):
            if not is_pkg:
                exec('import %s.%s as package' % (package_name, modname))
                views = locals()['package']
                for item in dir(views):
                    # call [hasattr] function of flask's request and session(werkzeug.local.LocalProxy),
                    # will be raise "RuntimeError: working outside of request context".
                    if item in ['request', 'session'] and getattr(views, item).__class__.__name__ == 'LocalProxy':
                        continue
                    view = getattr(views, item)
                    if hasattr(view, 'parameters') and hasattr(view, 'requisite') and view != CView:
                        name = class_name_to_api_name(view.__name__)
                        uri = '/%s/%s' % (package_name, name)
                        endpoint = '%s.%s' % (package_name, name)
                        app.add_url_rule(uri, view_func=view.as_view(endpoint, app))
