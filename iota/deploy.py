#
# (C) Copyright 2020 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
import base64
import functools
import json
import nacl.pwhash
import nacl.utils
import os
import re

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    request,
    session,
    url_for
)
from flask_api import status

from iota.token import verify

bp = Blueprint('deploy', __name__, url_prefix='/api/v1/deploy')

@bp.route('/firmware', methods=['PUT'])
def deploy_firmware():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy' : 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    return {}


@bp.route('/local_config', methods=['PUT'])
def deploy_local_config():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy' : 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    chip_id = request.headers.get("X-chip-id")
    if not chip_id:
        return {'local_config' : 'no CHIP ID given'}, status.HTTP_404_NOT_FOUND

    local_conf = None
    config_file = os.path.join(current_app.instance_path,
                               "config.json.%s" % (chip_id))
    try:
        with open(config_file, "rb") as f:
            local_conf = f.read()
    except OSError:
        local_conf = b"{'config_version': 0}"

    j = None
    try:
        j = json.loads(local_conf)
    except json.JSONDecodeError as e:
        j = {'config_version': 0}

    new_config = request.get_json()

    if "config_version" in new_config.keys() and \
            int(new_config['config_version']) <= int(j["config_version"]):
        return {'local_config' : 'new version <= current version'}, \
            status.HTTP_404_NOT_FOUND

    try:
        with open(config_file, "w") as f:
            json.dump(new_config, f, indent=4)
    except OSError as eos:
        print(eos)
        return {'local_config': 'failed to write config'}, \
            status.HTTP_500_INTERNAL_SERVER_ERROR

    return {'local_config': 'sucessfully deployed'}


@bp.route('/global_config', methods=['PUT'])
def deploy_global_config():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy' : 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    key = request.headers.get("X-global-config-key")
    if not key:
        return {'global_config' : 'no key supplied'}, status.HTTP_403_FORBIDDEN

    key = base64.b64decode(key)
    if len(key) != 32:
        return {'global_config' : 'invalid key'}, status.HTTP_403_FORBIDDEN

    global_conf = None
    config_file = os.path.join(current_app.instance_path, "global_config.enc")
    try:
        with open(config_file, "rb") as f:
            global_conf = f.read()
    except OSError:
        pass

    box = nacl.secret.SecretBox(key)
    if global_conf:
        global_conf = box.decrypt(global_conf)
    else:
        global_conf = b"{}"

    j = None
    try:
        j = json.loads(global_conf.decode("utf-8"))
    except json.JSONDecodeError as e:
        j = {'config_version': 0}

    new_config = request.get_json()
    if not "global_config_version" in new_config.keys():
        return {"global_config": "no version in new file"},\
            status.HTTP_400_BAD_REQUEST

    new_version = int(new_config['global_config_version'])
    if "global_config_version" in j.keys():
        current_version = int(j["global_config_version"])
    else:
        current_version = 0

    if new_version <= current_version:
        return {'global_config' : 'new version <= current version'}, \
            status.HTTP_304_NOT_MODIFIED

    try:
        with open(config_file, "wb") as f:
            plaintext = json.dumps(new_config, indent=4).encode("utf-8")
            f.write(box.encrypt(plaintext))
    except OSError as eos:
        print(eos)
        return {'global_config': 'failed to write config'},\
            status.HTTP_500_INTERNAL_SERVER_ERROR

    return {'global_config': 'sucessfully deployed'}, status.HTTP_201_CREATED
