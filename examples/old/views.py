# -*- coding: utf-8 -*-

import os
import logging
from flask import session
from fair import CView, Int, Str, Mail

from old import app

log = logging.getLogger(__name__)


class Area(CView):

    def get(self, area_id):
        """Get the area information through it's id.

        Detail info for api ...

        :plugin: json_p
        :param Int * area_id: Area id's description ...
        :raise id_not_exist: Record does not exist.
        """
        if area_id > 100:
            return self.r('id_not_exist')
        else:
            return self.r('success', {'id': area_id, 'name': 'area_%d' % area_id, 'superior': 0})


class UserInfo(CView):

    def get(self, user_id):
        """Get the user information through his/hers id.

        :plugin: json_p
        :param Int * user_id:
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
        return self.r('success', {'id': 1,
                                  'username': username,
                                  'nickname': nickname,
                                  'password': password,
                                  'email': email,
                                  'address': address,
                                  'mobile': mobile,
                                  'zipcode': zipcode})


class UserForExternal(CView):

    def get(self, user_id):
        """Get the user information through his/hers id.

        :param Int user_id:
        :raise id_invalid: Id is invalid.
        :raise id_not_exist: Record does not exist.
        """
        if user_id < 1:
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


