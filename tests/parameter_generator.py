# -*- coding: utf-8 -*-

from api import app, request
from api.plugin import Token


@app.route('/parameter_generator/token/', endpoint='parameter_generator.token')
def token():
    identity = request.args.get('identity')
    tests_access_key = request.args.get('tests_access_key')
    if not identity:
        return '/parameter_generator/token/ must specify the parameter [identity]'
    if not tests_access_key:
        return '/parameter_generator/token/ must specify the parameter [tests_access_key]'
    if tests_access_key not in app.config['tests_access_keys']:
        return 'invalid tests_access_key'
    return Token.create(identity)
