import time
import base64
import binascii
from Crypto.Cipher import AES

from http_api.parameter import Str
from http_api.plugin import Plugin, NOT_NULL
from http_api.plugin.jsonp import JsonPRaise
from http_api.utility import get_cls_with_path


class TokenException(Exception):
    """All Token exception's parent class"""


class TokenTimestampInvalid(TokenException):
    """Token timestamp invalid, timestamp must be integer"""


class TokenTimeout(TokenException):
    """Token time out"""


class TokenInvalid(TokenException):
    """Token invalid"""


class TokenKeyInvalid(TokenException):
    """Token key must be 16 bytes long"""


PARAM_TOKEN = 'token'
PARAM_IDENTITY = 'identity'
TOKEN_TIME_OUT = 60             # 1 minute


class Token(Plugin):
    """Token check Plugin.

    :cvar function __key_provider: provide token secret key by identity
            e.g.:
            def key_provider(identity):
                \"""Provide token secret key by identity.

                :param str identity: Username or App Id
                :return: str. secret key, length must be 16
                \"""
                key = b'not implemented '
                return key.decode() if type(key) == bytes else key
    """
    error_codes = {'token_invalid': 'Invalid Token'}

    parameters = (
        (PARAM_IDENTITY, Str, NOT_NULL, 'Identity'),
        (PARAM_TOKEN, Str, NOT_NULL, 'Token')
    )

    def __init__(self, params):
        self.__key_provider = get_cls_with_path(params['key_provider'])
        self.__raise_class = get_cls_with_path(params['raise_class'])

    # def init_view(self, view_class, method):
    #     del method.element.param_default[PARAM_TOKEN]
    #     del method.element.param_default[PARAM_IDENTITY]

    def before_request(self, view):
        if hasattr(view, 'json_p_callback_name'):
            self.__raise_class = JsonPRaise
        # get token parameter
        token = view.params.get(PARAM_TOKEN)
        identity = view.params.get(PARAM_IDENTITY)
        if not token:
            raise self.__raise_class(view, 'token_invalid', {'error': 'param_missing', 'parameter': PARAM_TOKEN})
        if not identity:
            raise self.__raise_class(view, 'token_invalid', {'error': 'param_missing', 'parameter': PARAM_IDENTITY})
        # check token
        try:
            self.check(identity, token)
        except TokenException as e:
            raise self.__raise_class(view, 'token_invalid', {'error': str(e)})

    def create(self, identity, timestamp=None):
        """Generate token use identity and timestamp.

        :param str identity: Username or App Id
        :param int timestamp: Current or specific timestamp

        :return: str. token

        :raise TokenTimestampInvalid: Token timestamp invalid, timestamp must be integer
        :raise TokenKeyInvalid: Key must be 16 bytes long
        """
        key = self.__key_provider(identity)
        try:
            plaintext = '%d%s' % (timestamp or int(time.time()), key.decode())
        except TypeError:
            raise TokenTimestampInvalid('Token timestamp invalid, timestamp must be integer')
        # plaintext must be a multiple of 16 in length
        fill_size = 16 - len(plaintext) % 16
        byte_text = plaintext.encode() + b'\x00' * (0 if fill_size == 16 else fill_size)
        try:
            aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + b'x')
        except ValueError:
            raise TokenKeyInvalid('Key must be 16 bytes long')
        cipher_text = aes_obj.encrypt(byte_text)
        return base64.b16encode(cipher_text).decode()

    def check(self, identity, cipher_text):
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
        key = self.__key_provider(identity)
        try:
            aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + b'x')
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
