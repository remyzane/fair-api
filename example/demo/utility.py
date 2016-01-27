# -*- coding: utf-8 -*-

import os
import base64
from Crypto.Cipher import AES

from http_api.utility import load_yaml

demo_key = b'p' * 16
demo_iv = b'i' * 16
program_dir = os.path.realpath(os.path.join(__file__, '..', '..'))


def get_config(path, file_name):
    config_file = os.path.join(path, file_name)
    if not os.path.exists(config_file):
        raise Exception('config file [%s] not exists.' % config_file)
    return load_yaml(config_file)


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
