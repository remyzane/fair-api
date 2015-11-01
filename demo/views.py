# -*- coding: utf-8 -*-

import os
import logging
from peewee import CharField, Model

from api import app, session, Api, Int, Str, Mob, Mail, Zipcode, Username, Password
from api.plugin import Token
from demo import SimpleAes

log = logging.getLogger(__name__)


class GetArea(Api):
    description = '''查询地区（通过地区ID）'''
    parameters = {'id': Int}
    requisite = ('id',)
    json_p = 'callback'
    plugins_exclude = (Token,)
    codes = {
        'id_not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        if user_id > 100:
            return self.result('id_not_exist')
        else:
            return self.result('success', {'id': user_id,
                                           'name': 'area_%d' % user_id,
                                           'superior': 0})


class GetUser(Api):
    description = '''查询用户（通过用户ID）'''
    parameters = {'identity': Str, 'token': Str, 'id': Int}
    requisite = ('identity', 'token', 'id',)
    json_p = 'callback'
    codes = {
        'id_not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        if user_id > 100:
            return self.result('id_not_exist')
        else:
            return self.result('success', {'id': user_id,
                                           'name': 'user_%d' % user_id,
                                           'email': 'user_%s@yourself.com' % user_id})


class GetUser(Api):
    description = '''查询用户（通过用户ID）'''
    parameters = {'identity': Str, 'token': Str, 'id': Int}
    requisite = ('identity', 'token', 'id',)
    json_p = 'callback'
    codes = {
        'id_not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        if user_id > 100:
            return self.result('id_not_exist')
        else:
            return self.result('success', {'id': user_id,
                                           'name': 'user_%d' % user_id,
                                           'email': 'user_%s@yourself.com' % user_id})


class GetUserForExternal(Api):
    description = '''查询用户（通过用户ID密文）'''
    parameters = {'id': Str}
    requisite = ('id',)
    plugins_exclude = (Token,)
    codes = {
        'id_invalid': '无效的Id',
        'id_not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        user_id = SimpleAes.decrypt(user_id)
        if not user_id:
            return self.result('id_invalid', {'error': 'Unable to decrypt'})
        try:
            user_id = int(user_id)
        except ValueError:
            return self.result('id_invalid', {'error': 'id must be integer', 'id': user_id})

        if user_id > 100:
            return self.result('id_not_exist')
        else:
            return self.result('success', {'id': user_id,
                                           'name': 'user_%d' % user_id,
                                           'email': 'user_%s@yourself.com' % user_id})


class SetUser(Api):
    description = '''设置用户'''
    parameters = {'identity': Str, 'token': Str, 'username': Username, 'nickname': Str,
                  'password': Password, 'email': Mail, 'address': Str, 'mobile': Mob, 'zipcode': Zipcode}
    requisite = ('identity', 'token', 'username', 'password', 'email')
    codes = {
        'mobile_existent': '手机号已经存在',
        'email_existent': '邮箱地址已经存在'
    }

    def post(self, params):
        self.process_log += 'do job 1' + os.linesep
        self.process_log += 'do job 2' + os.linesep
        self.process_log += 'do job 3'
        return self.result('success', {'id': 1})


class Session(Api):
    description = '''Session测试'''
    plugins_exclude = (Token,)
    codes = {
        'not_configured': '系统未配置Session, 请启用api.yml中的SECRET_KEY',
        'not_login': '未登录'
    }

    def get(self, params):
        if not app.config.get('SECRET_KEY'):
            return self.result('not_configured')
        if not session.get('user'):
            return self.result('not_login')

        return self.result('success', {'key': session['user']})


class User(Model):
    username = CharField()


class Performance(Api):
    description = '''性能测试'''
    plugins_exclude = (Token,)

    def get(self, params):
        for index in range(1, 100):
            id = index % 100 or 1
            username = User.get(User.id == id).username
        return self.result('success')
