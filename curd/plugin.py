# -*- coding: utf-8 -*-

import time
import base64
import binascii
from Crypto.Cipher import AES

from .view import CView, RR


class Plugin(object):
    """API Plugin parent class.

    :cvar codes: error code and message
    :type codes: dict
    """
    codes = {}

    @classmethod
    def do(cls, api):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param api: Api class instance
        :type  api: CView

        :raise NotImplementedError: Plugin must have [do] method
        """
        raise NotImplementedError('Plugin must have [do] method.')


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

    :cvar codes: error code and message
    :type codes: dict
    """
    codes = {'token_invalid': 'Invalid Token'}

    @classmethod
    def do(cls, api):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param api: Api class instance for request
        :type  api: Api

        :raise RR: RaiseResponse
        """
        # get token parameter
        token = api.params.get(PARAM_TOKEN)
        identity = api.params.get(PARAM_IDENTITY)
        if not token:
            raise RR(api.result('token_invalid', {'error': 'param_missing', 'parameter': PARAM_TOKEN}))
        if not identity:
            raise RR(api.result('token_invalid', {'error': 'param_missing', 'parameter': PARAM_IDENTITY}))
        # check token
        try:
            cls.check(identity, token)
        except TokenException as e:
            raise RR(api.result('token_invalid', {'error': str(e)}))

    @classmethod
    def get_key(cls, identity):
        """Get secret key by identity.

        :param identity: Username or App Id
        :type  identity: str

        :return: secret key, length must be 16
        :rtype: str
        """
        key = 'not implemented '    # TODO implement yourself

        return key.decode() if type(key) == bytes else key

    @classmethod
    def create(cls, identity, timestamp=None):
        """Generate token use identity and timestamp.

        :param identity: Username or App Id
        :type  identity: str
        :param timestamp: Current or specific timestamp
        :type  timestamp: int

        :return: token
        :rtype: str

        :raise TokenTimestampInvalid: Token timestamp invalid, timestamp must be integer
        :raise TokenKeyInvalid: Key must be 16 bytes long
        """
        key = cls.get_key(identity)
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

        :param identity: Username or App Id
        :param cipher_text: Token value
        :return: Token Valid or Invalid
        :rtype: bool

        :raise TokenInvalid: Token invalid
        :raise TokenKeyInvalid: Key must be 16 bytes long
        :raise TokenTimeout: Token time out
        """
        if len(cipher_text) % 16 != 0:
            raise TokenInvalid('Token must be a multiple of 16 in length')
        key = cls.get_key(identity)
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