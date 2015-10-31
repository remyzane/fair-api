# -*- coding: utf-8 -*-

import time
import pytest
import base64
from Crypto.Cipher import AES

from api.plugin import Token, TokenInvalid, TokenTimeout, TokenKeyInvalid, TOKEN_TIME_OUT


def test_token():
    identity = 'one user'
    Token._unit_test_key = b'p' * 16

    pytest.raises(TokenInvalid, Token.create, 'plaintext', 'error timestamp')

    timestamp = int(time.time())
    assert Token.create(identity, timestamp) == Token.create(identity, timestamp)
    assert Token.create(identity, timestamp) != Token.create(identity, timestamp + 1)

    cipher_text = Token.create(identity)
    assert Token.check(identity, cipher_text) == True

    cipher_text = Token.create(identity, timestamp - TOKEN_TIME_OUT)
    pytest.raises(TokenTimeout, Token.check, identity, cipher_text)

    key = Token.get_key(identity)
    aes_obj = AES.new(key, AES.MODE_CBC, key[1:] + 'x')
    cipher_text = base64.b16encode(aes_obj.encrypt('error timestamp '))
    pytest.raises(TokenInvalid, Token.check, identity, cipher_text)

    Token._unit_test_key = b't' * 16
    pytest.raises(TokenInvalid, Token.check, identity, cipher_text)

    # error key
    Token._unit_test_key = b'p' * 13
    pytest.raises(TokenKeyInvalid, Token.create, identity)
    pytest.raises(TokenKeyInvalid, Token.check, identity, cipher_text)
