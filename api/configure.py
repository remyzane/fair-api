# -*- coding: utf-8 -*-

import peewee
import logging
import pkgutil
import datetime

from .utility import class_name_to_api_name

log = logging.getLogger(__name__)

types = {
    'mysql': peewee.MySQLDatabase,
    'pgsql': peewee.PostgresqlDatabase,
    'sqlite': peewee.SqliteDatabase
}
db = {}


# configure database (execution of this config must preceded view and model import)
def set_database(config):
    global db
    for database in config:
        db[database['key']] = types[database['type']](**config[0]['params'])
    # set default db
    peewee.Model._meta.database = db.get('default') or db[0]


# configure flask (app.config) defined in app section at api.yml
def set_flask(app, config):
    # config item
    for name in config:
        # set the expiration date of a permanent session.
        if name == 'PERMANENT_SESSION_LIFETIME':
            app.config[name] = datetime.timedelta(days=int(config[name]))
        else:
            # other config
            app.config[name] = config[name]


# 设置view
def set_view(app, config):
    from .api import Api
    app.view_packages = config
    for package_name in app.view_packages:
        exec('import %s as package' % package_name)
        # 遍历包中的所有文件和子目录
        for importer, modname, is_pkg in pkgutil.iter_modules(locals()['package'].__path__):
            if not is_pkg:
                exec('import %s.%s as package' % (package_name, modname))
                views = locals()['package']
                for item in dir(views):
                    # 在这里对flask的request和session(werkzeug.local.LocalProxy)进行hasattr操作
                    # 会抛"RuntimeError: working outside of request context"异常
                    if item in ['request', 'session'] and getattr(views, item).__class__.__name__ == 'LocalProxy':
                        continue

                    view = getattr(views, item)
                    if hasattr(view, 'parameters') and hasattr(view, 'requisite') and view != Api:
                        name = class_name_to_api_name(view.__name__)
                        uri = '/%s/%s' % (package_name, name)
                        endpoint = '%s.%s' % (package_name, name)
                        app.add_url_rule(uri, view_func=view.as_view(endpoint))
