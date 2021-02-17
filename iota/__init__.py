#
# (C) Copyright 2020 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
from flask import Flask
import os

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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
