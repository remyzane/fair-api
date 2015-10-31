# -*- coding: utf-8 -*-

from api import app, request


@app.route('/parameter_generator/token/', endpoint='parameter_generator.token')
def generate():
    identity = request.args.get('identity')
    return identity # TODO
