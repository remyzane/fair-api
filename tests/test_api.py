# -*- coding: utf-8 -*-

import time
import pytest
import base64
from mock import MagicMock
from Crypto.Cipher import AES

from curd.plugin import Token, TokenInvalid, TokenTimeout, TokenKeyInvalid, TOKEN_TIME_OUT


def test_token():
    identity = 'somebody'
    Token.get_key = MagicMock()
    Token.get_key.return_value = 'p' * 16

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

    Token.get_key.return_value = 't' * 16
    pytest.raises(TokenInvalid, Token.check, identity, cipher_text)

    # error key
    Token.get_key.return_value = 'p' * 13
    pytest.raises(TokenKeyInvalid, Token.create, identity)
    pytest.raises(TokenKeyInvalid, Token.check, identity, cipher_text)
