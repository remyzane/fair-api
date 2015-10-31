# -*- coding: utf-8 -*-

from api import app, request


@app.route('/token/generate/', endpoint='token.generate')
def generate():
    identity = request.args.get('identity')
    return identity # TODO
