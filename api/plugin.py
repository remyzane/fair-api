# -*- coding: utf-8 -*-

import time
import base64
import binascii
from Crypto.Cipher import AES

from .api import RR


class Plugin(object):
    codes = {}


class TokenException(Exception):
    pass


class TokenTimeout(TokenException):
    pass


class TokenInvalid(TokenException):
    pass


class TokenKeyInvalid(TokenException):
    pass


PARAM_TOKEN = 'token'
PARAM_IDENTITY = 'identity'
TOKEN_TIME_OUT = 60


class Token(Plugin):
    codes = {'token_invalid': 'Token校样无效'}

    @staticmethod
    def do(api):
        # 判断是否设置不做token检查
        if hasattr(api, 'no_token'):
            return
        # 参数检查
        if not api.params.get(PARAM_IDENTITY):
            raise RR(api.result('token_invalid', {'error': 'param_missing', 'parameter': PARAM_IDENTITY}))
        if not api.params.get(PARAM_TOKEN):
            raise RR(api.result('token_invalid', {'error': 'param_missing', 'parameter': PARAM_TOKEN}))

        raise RR(api.result('token_invalid', {'error': 'aaa'}))

    # unit test use only
    _unit_test_key = None

    # 要求密钥长度使用16
    @classmethod
    def get_key(cls, identity):
        if cls._unit_test_key:
            key = cls._unit_test_key
        else:
            key = 'not implemented '    # TODO implement yourself

        # 必须返回unicode字串
        return key.decode() if type(key) == bytes else key

    @classmethod
    def create(cls, identity, timestamp=None):
        key = cls.get_key(identity)
        try:
            plaintext = '%d%s' % (timestamp or int(time.time()), key)
        except TypeError:
            raise TokenInvalid('Token invalid, timestamp must be integer')
        # 加密算法要求数据长度必须是密钥长度的倍数
        fill_size = 16 - len(plaintext) % 16
        byte_text = plaintext.encode() + b'\x00' * (0 if fill_size == 16 else fill_size)
        try:
            aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + 'x')
        except ValueError:
            raise TokenKeyInvalid('Key must be 16 bytes long')
        cipher_text = aes_obj.encrypt(byte_text)
        return base64.b16encode(cipher_text)

    @classmethod
    def check(cls, identity, cipher_text):
        key = cls.get_key(identity)
        try:
            aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + 'x')
        except ValueError:
            raise TokenKeyInvalid('Key must be 16 bytes long')
        try:
            byte_text = aes_obj.decrypt(base64.b16decode(cipher_text, True)).rstrip(b'\x00')
            plaintext = byte_text[: -16]
        except binascii.Error:                  # base64 raise
            raise TokenInvalid('Token invalid')
        try:
            # 检测有效时间
            if time.time() - int(plaintext) > TOKEN_TIME_OUT:
                raise TokenTimeout('Token time out')
        except ValueError:
            raise TokenInvalid('Token invalid, must be timestamp')
        return True