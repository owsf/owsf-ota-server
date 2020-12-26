#
# (C) Copyright 2020 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
from flask import Flask, request, json, escape
from flask_api import status
from packaging.version import parse as parse_version
import base64
import json
import nacl.secret
import nacl.utils
import os

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
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

    @app.route('/api/v1/global_config')
    def gconfig():
        version = request.headers.get("X-global-config-version")
        if not version:
            return {'global_config' : 'no version given'}, status.HTTP_404_NOT_FOUND

        key = request.headers.get("X-global-config-key")
        if not key:
            return {'global_config' : 'no key supplied'}, status.HTTP_403_FORBIDDEN

        key = base64.b64decode(key)
        if len(key) != 32:
            return {'global_config' : 'invalid key'}, status.HTTP_403_FORBIDDEN

        ctext = None
        try:
            with open(os.path.join(app.instance_path, "global_config.enc"), "rb") as f:
                ctext = f.read()
        except OSError:
            return {'global_config' : 'invalid key'}, status.HTTP_503_SERVICE_UNAVAILABLE

        box = nacl.secret.SecretBox(key)
        plaintext = box.decrypt(ctext)

        j = None
        try:
            j = json.loads(plaintext.decode("utf-8"))
        except json.JSONDecodeError as e:
            return {'global_config' : 'failed to load'}, status.HTTP_403_FORBIDDEN

        if int(version) >= int(j["global_config_version"]):
            return {'global_config' : 'no version new version'}, status.HTTP_404_NOT_FOUND

        return plaintext, status.HTTP_200_OK

    @app.route('/api/v1/local_config')
    def lconfig():
        version = request.headers.get("X-config-version")
        if not version:
            return {'local_config' : 'no version given'}, status.HTTP_404_NOT_FOUND

        chip_id = request.headers.get("X-chip-id")
        if not chip_id:
            return {'local_config' : 'no CHIP ID given'}, status.HTTP_404_NOT_FOUND

        local_conf = None
        try:
            with open(os.path.join(app.instance_path, "config.json.%s" % (chip_id)), "rb") as f:
                local_conf = f.read()
        except OSError:
            return {'local_config' : 'config for chip id not found'}, status.HTTP_404_NOT_FOUND

        j = None
        try:
            j = json.loads(local_conf)
        except json.JSONDecodeError as e:
            return {'local_config' : 'failed to load'}, status.HTTP_500_INTERNAL_SERVER_ERROR
        if int(version) >= int(j["config_version"]):
            return {'local_config' : 'no version new version'}, status.HTTP_404_NOT_FOUND

        return local_conf, status.HTTP_200_OK


    @app.route('/api/v1/firmware')
    def firmware():
        version = request.headers.get("X-ESP8266-version")
        if not version:
            return {'firmware' : 'no version given'}, status.HTTP_404_NOT_FOUND

        try:
            with open(os.path.join(app.instance_path, "firmware.json")) as f:
                j = json.load(f)
        except OSError:
            return {}, status.HTTP_404_NOT_FOUND
        except json.JSONDecodeError as e:
            return {}, status.HTTP_404_NOT_FOUND

        vremote = None
        vlocal = None
        try:
            vlocal = parse_version(j["version"])
        except ValueError:
            pass

        try:
            vremote = parse_version(version)
        except ValueError:
            pass

        if vremote and vlocal and vremote >= vlocal :
            return {}, status.HTTP_304_NOT_MODIFIED

        try:
            ffile = j["file"]
        except ValueError:
            return {}, status.HTTP_404_NOT_FOUND

        if ffile[0] != "/":
            if not os.path.exists(os.path.join(app.instance_path, ffile)):
                return {'firmware': "not found"}, status.HTTP_404_NOT_FOUND
            else:
                ffile = os.path.join(app.instance_path, ffile)

        if ffile[0] == "/" and not os.path.exists(ffile):
            return {'firmware': "not found"}, status.HTTP_404_NOT_FOUND

        with open(ffile, "rb") as f:
            fw = f.read()

        return fw, status.HTTP_200_OK

    return app
