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
    try:
        with open(os.path.join(current_app.instance_path, "config.json.%s" % (chip_id)), "rb") as f:
            local_conf = f.read()
    except OSError:
        local_conf = b"{'config_version': 0}"

    j = None
    try:
        j = json.loads(local_conf)
    except json.JSONDecodeError as e:
        j = {'config_version': 0}

    new_config = request.get_json()

    if "config_version" in new_config.keys() and int(new_config['config_version']) <= int(j["config_version"]):
        return {'local_config' : 'new version <= current version'}, status.HTTP_404_NOT_FOUND

    try:
        with open(os.path.join(current_app.instance_path, "config.json.%s" % (chip_id)), "w") as f:
            json.dump(new_config, f, indent=4)
    except OSError as eos:
        print(eos)
        return {'local_config': 'failed to write config'}, status.HTTP_500_INTERNAL_SERVER_ERROR

    return {'local_config': 'sucessfully deployed'}

@bp.route('/global_config', methods=['PUT'])
def deploy_global_config():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy' : 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    return {}
