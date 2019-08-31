# -*- coding: utf-8 -*-

def get_token_key(identity):
    """Provide token secret key by identity.

    :param str identity: Username or App Id
    :return: str. secret key, length must be 16
    """
    key = b'not implemented '    # TODO implement yourself

    return key if type(key) == bytes else key.encode()
