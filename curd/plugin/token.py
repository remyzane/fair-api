# -*- coding: utf-8 -*-

import time
import base64
import binascii
from Crypto.Cipher import AES

from curd.plugin import Plugin
from curd.view import RR, CView


class TokenException(Exception):
    pass


class TokenTimestampInvalid(TokenException):
    pass


class TokenTimeout(TokenException):
    pass


class TokenInvalid(TokenException):
    pass


class TokenKeyInvalid(TokenException):
    pass


PARAM_TOKEN = 'token'
PARAM_IDENTITY = 'identity'
TOKEN_TIME_OUT = 60             # 1 minute


class Token(Plugin):
    """Token check Plugin.

    :cvar dict error_codes: error code and message
    :cvar function __key_provider: provide token secret key by identity
    """
    error_codes = {'token_invalid': 'Invalid Token'}

    @staticmethod
    def __key_provider(identity):
        """Provide token secret key by identity.

        :param str identity: Username or App Id
        :return: str. secret key, length must be 16
        """
        key = 'not implemented '
        return key.decode() if type(key) == bytes else key

    @classmethod
    def reconstruct(cls, params):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param dict params: plug config parameters
        """
        exec('from %s import %s as key_provider' % tuple(params['key_provider'].rsplit('.', 1)))
        cls.__key_provider = locals()['key_provider']

    @classmethod
    def init_view(cls, view_class):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view_class: view class
        """
        pass

    def aaa(self, i):
        """Get index

        :param i: index
        :return: index
        """

        return i

    @classmethod
    def before_request_aa(cls, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: Api class instance for request
        :return:
        :raise RR: RaiseResponse
        """

        # get token parameter
        token = view.params.get(PARAM_TOKEN)
        identity = view.params.get(PARAM_IDENTITY)
        if not token:
            raise RR(view.result('token_invalid', {'error': 'param_missing', 'parameter': PARAM_TOKEN}))
        if not identity:
            raise RR(view.result('token_invalid', {'error': 'param_missing', 'parameter': PARAM_IDENTITY}))
        # check token
        try:
            cls.check(identity, token)
        except TokenException as e:
            raise RR(view.result('token_invalid', {'error': str(e)}))

    @classmethod
    def create(cls, identity, timestamp=None):
        """Generate token use identity and timestamp.

        :param str identity: Username or App Id
        :param int timestamp: Current or specific timestamp

        :return: str. token

        :raise TokenTimestampInvalid: Token timestamp invalid, timestamp must be integer
        :raise TokenKeyInvalid: Key must be 16 bytes long
        """
        key = cls.__key_provider(identity)
        try:
            plaintext = '%d%s' % (timestamp or int(time.time()), key)
        except TypeError:
            raise TokenTimestampInvalid('Token timestamp invalid, timestamp must be integer')
        # plaintext must be a multiple of 16 in length
        fill_size = 16 - len(plaintext) % 16
        byte_text = plaintext.encode() + b'\x00' * (0 if fill_size == 16 else fill_size)
        try:
            aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + 'x')
        except ValueError:
            raise TokenKeyInvalid('Key must be 16 bytes long')
        cipher_text = aes_obj.encrypt(byte_text)
        return base64.b16encode(cipher_text).decode()

    @classmethod
    def check(cls, identity, cipher_text):
        """Check Token is valid or invalid.

        :param str identity: Username or App Id
        :param str cipher_text: Token value
        :return: bool. Token Valid or Invalid

        :raise TokenInvalid: Token invalid
        :raise TokenKeyInvalid: Key must be 16 bytes long
        :raise TokenTimeout: Token time out
        """
        if len(cipher_text) % 16 != 0:
            raise TokenInvalid('Token must be a multiple of 16 in length')
        key = cls.__key_provider(identity)
        try:
            aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + 'x')
        except ValueError:
            raise TokenKeyInvalid('Key must be 16 bytes long')
        try:
            byte_text = aes_obj.decrypt(base64.b16decode(cipher_text, True)).rstrip(b'\x00')
            plaintext = byte_text[: -16]
        except binascii.Error:                      # base64 raise
            raise TokenInvalid('Token invalid')
        try:
            # check time
            if time.time() - int(plaintext) > TOKEN_TIME_OUT:
                raise TokenTimeout('Token time out')
        except ValueError:
            raise TokenInvalid('Token invalid, must be timestamp')
        return True
