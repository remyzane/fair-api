# -*- coding: utf-8 -*-

def get_token_key(identity):
    """Provide token secret key by identity.

    :param str identity: Username or App Id
    :return: str. secret key, length must be 16
    """
    key = 'not implemented '    # TODO implement yourself

    return key.decode() if type(key) == bytes else key
