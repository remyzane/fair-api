# -*- coding: utf-8 -*-

import os
import logging
from flask import session, request
from peewee import CharField, Model
from curd import CView, Int, Str, Mail

from demo import app
from .utility import SimpleAes

log = logging.getLogger(__name__)


class Area(CView):

    def get(self, area_id):
        """Get the area information through it's id.

        :plugin: json_p
        :param Int * area_id: area id
        :raise id_not_exist: Record does not exist.
        """
        if area_id > 100:
            return self.r('id_not_exist')
        else:
            return self.r('success', {'id': area_id, 'name': 'area_%d' % area_id, 'superior': 0})


class UserInfo(CView):

    def get(self, user_id):
        """Get the user information through his/hers id.

        :plugin: json_p token
        :param Str * identity:
        :param Str * token:
        :param Bool * user_id:
        :raise id_not_exist: Record does not exist.
        """
        if user_id > 100:
            return self.r('id_not_exist')
        else:
            return self.r('success', {'id': user_id,
                                           'name': 'user_%d' % user_id,
                                           'email': 'user_%s@yourself.com' % user_id})

    def post(self, username, nickname, password, email, address, mobile, zipcode):
        """User setting

        :plugin: token
        :param Str * identity: Identity
        :param Str * token: Token
        :param Bool * username:
        :param Str nickname:
        :param Str * password:
        :param Mail * email:
        :param Str address:
        :param Str mobile:
        :param Str zipcode:
        :raise mobile_existent: Mobile number already exists.
        :raise email_existent: Email address already exists.
        """
        self.process_log += 'do job 1' + os.linesep
        self.process_log += 'do job 2' + os.linesep
        self.process_log += 'do job 3'
        return self.r('success', {'id': 1})


class UserForExternal(CView):

    def get(self, user_id):
        """Get the user information through his/hers encrypted id.

        :param Str user_id:
        :raise id_invalid: Id is invalid.
        :raise id_not_exist: Record does not exist.
        """
        user_id = SimpleAes.decrypt(user_id)
        if not user_id:
            return self.r('id_invalid', {'error': 'Unable to decrypt'})
        try:
            user_id = int(user_id)
        except ValueError:
            return self.r('id_invalid', {'error': 'id must be integer', 'id': user_id})

        if user_id > 100:
            return self.r('id_not_exist')
        else:
            return self.r('success', {'id': user_id,
                                           'name': 'user_%d' % user_id,
                                           'email': 'user_%s@yourself.com' % user_id})


class Session(CView):

    def get(self):
        """Session testing.

        :raise not_configured: Session is not configured, Please setting SECRET_KEY in CView.yml.
        :raise not_login: Not logged in
        """
        if not app.config.get('SECRET_KEY'):
            return self.r('not_configured')
        if not session.get('user'):
            return self.r('not_login')

        return self.r('success', {'key': session['user']})


class User(Model):
    username = CharField()


class Performance(CView):

    def get(self):
        """The performance test
        """
        for index in range(1, 100):
            id = index % 100 or 1
            username = User.get(User.id == id).username
        return self.r('success')
