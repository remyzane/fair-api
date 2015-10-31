# -*- coding: utf-8 -*-

import logging

from api import Api, Int, Str
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
