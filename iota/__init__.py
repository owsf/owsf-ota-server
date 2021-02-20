#
# (C) Copyright 2020 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
"""IOTA -- a simple IOT OTA server

This module defines a simple server for IOT OTA updates of firmware and
configuration.
"""
from flask import Flask
import os


def create_app(test_config=None):
    try:
        instance_path = os.environ["IOTA_INSTANCE_PATH"]
    except :
        instance_path = os.path.join(os.environ["PWD"], "instance")

    app = Flask(__name__, instance_path=instance_path)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'iota.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/api/v1')
    def landing():
        return 'Hello, World!'

    from . import token
    app.register_blueprint(token.bp)

    from . import deploy
    app.register_blueprint(deploy.bp)

    from . import serve
    app.register_blueprint(serve.bp)

    from .db import init_app as db_init_app
    db_init_app(app)

    return app
