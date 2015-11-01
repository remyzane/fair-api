# -*- coding: utf-8 -*-

import base64
from Crypto.Cipher import AES


demo_key = b'p' * 16
demo_iv = b'i' * 16


class SimpleAes(object):

    @staticmethod
    def encrypt(data, key=demo_key, iv=demo_iv):
        fill_size = 16 - len(data) % 16
        byte_text = data.encode() + b'\x00' * (0 if fill_size == 16 else fill_size)
        aes_obj = AES.new(key, AES.MODE_CBC, iv)
        cipher_text = aes_obj.encrypt(byte_text)
        return base64.b16encode(cipher_text)

    @staticmethod
    def decrypt(data, key=demo_key, iv=demo_iv):
        if len(data) % 16 != 0:
            return None
        aes_obj = AES.new(key, AES.MODE_CBC, iv)
        bytes_data = aes_obj.decrypt(base64.b16decode(data, True)).rstrip(b'\x00')
        return bytes_data.decode()
