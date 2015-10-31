# -*- coding: utf-8 -*-

import os
import logging
from peewee import CharField, Model

from api import Api, Int, Str, Mob, Mail, Zipcode
from api.plugin import Token

log = logging.getLogger(__name__)


class GetArea(Api):
    description = '''查询地区（通过地区ID）'''
    parameters = {'id': Int}
    requisite = ('id',)
    json_p = 'callback'
    plugins_exclude = (Token,)
    codes = {
        'not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        if user_id > 100:
            return self.result('not_exist')
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
        'not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        if user_id > 100:
            return self.result('not_exist')
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
        'not_exist': '记录不存在'
    }

    def get(self, params):
        user_id = params['id']
        if user_id > 100:
            return self.result('not_exist')
        else:
            return self.result('success', {'id': user_id,
                                           'name': 'user_%d' % user_id,
                                           'email': 'user_%s@yourself.com' % user_id})


class SetUser(Api):
    description = '''查询用户（通过用户ID）'''
    parameters = {'identity': Str, 'token': Str, 'username': Str, 'nickname': Str, 'email': Mail, 'address': Str,
                  'mobile': Mob, 'zipcode': Zipcode}
    requisite = ('identity', 'token', 'username', 'email')
    codes = {
        'mobile_existent': '手机号已经存在',
        'email_existent': '邮箱地址已经存在'
    }

    def post(self, params):
        self.process_log += 'do job 1' + os.linesep
        self.process_log += 'do job 2' + os.linesep
        self.process_log += 'do job 3'
        return self.result('success', {'id': 1})


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
