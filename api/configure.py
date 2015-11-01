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


# 设置数据库(必须先于model导入之前调用)
def set_database(config):
    global db
    for database in config:
        db[database['key']] = types[database['type']](**config[0]['params'])
    # model 不指定时database, 默认使用default或配置的第一个数据库
    peewee.Model._meta.database = db.get('default') or db[0]


# 设置Flask配置（app.config）通过mail.yml中的app配置段
def set_flask(app, config):
    # 配置系统
    for name in config:
        # Flask内置设置，保留用户session几天（登陆页面用户选择以后免登陆时，系统保留登录状态的天数）
        if name == 'PERMANENT_SESSION_LIFETIME':
            app.config[name] = datetime.timedelta(days=int(config[name]))
        else:
            # 保存配置信息，由系统其它地方使用
            app.config[name] = config[name]     # copy.deepcopy() 无需复制全新数据


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
