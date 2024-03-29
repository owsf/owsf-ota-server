#
# (C) Copyright 2020 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
import base64
import json
import nacl.pwhash
import nacl.utils
import os
import re

from flask import (
    Blueprint,
    current_app,
    request,
)
from flask_api import status

from iota.token import verify


def _verprep(v):
    v = v.lstrip().rstrip()
    v = re.sub(r"[^0-9._+-]+?", "", v)
    return v


def v2l(v):
    as_list = v.split(".")
    for i in range(0, len(as_list)):
        as_list[i] = re.sub(r"[_+-]+?", ".", as_list[i])
        as_list[i] = as_list[i].split(".")

    for i in range(0, len(as_list)):
        for j in range(0, len(as_list[i])):
            if re.match(r"[0-9]+", as_list[i][j]):
                as_list[i][j] = int(as_list[i][j])

    return as_list


def vercmp(v1, v2):
    v1 = v2l(_verprep(v1))
    v2 = v2l(_verprep(v2))

    cmp = 0
    for i in range(0, min(len(v1), len(v2))):
        for j in range(0, min(len(v1[i]), len(v2[i]))):
            if v1[i][j] < v2[i][j]:
                cmp = 1
                break
            elif v1[i][j] > v2[i][j]:
                cmp = -1
                break
        if cmp == 0 and len(v1[i]) != len(v2[i]):
            cmp = 1 if len(v1) < len(v2) else -1
        if cmp != 0:
            break

    if cmp == 0 and len(v1) == len(v2):
        return 0
    elif cmp == 0 and len(v1) != len(v2):
        return 1 if len(v1) < len(v2) else -1
    else:
        return cmp


bp = Blueprint('deploy', __name__, url_prefix='/api/v1/deploy')


@bp.route('/firmware', methods=['PUT'])
def deploy_firmware():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy': 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    new_version = request.headers.get("X-firmware_version")
    if not new_version:
        return {"deploy": "no firmware version specified"},\
            status.HTTP_400_BAD_REQUEST

    config_file = os.path.join(current_app.instance_path, "firmware.json")
    try:
        with open(config_file, "rb") as f:
            j = json.load(f)
    except OSError:
        j = {"version": "0.0"}
    except json.JSONDecodeError:
        j = {"version": "0.0"}

    if "version" in j.keys():
        current_version = j["version"]

    if vercmp(current_version, new_version) <= 0:
        return {'deploy': 'current firmware version >= new firmware version'},\
            status.HTTP_304_NOT_MODIFIED

    new_firmware = base64.b64decode(request.get_data())
    # TODO test signature
    firmware_name = "firmware.sig"
    firmware_file = os.path.join(current_app.instance_path, firmware_name)
    j = {"version": new_version, "file": firmware_name}
    try:
        with open(firmware_file, "wb") as f:
            f.write(new_firmware)
        with open(config_file, "w") as f:
            f.write(json.dumps(j, indent=4))
    except OSError as e:
        print(e)
        return {"firmware": "failed to write new firmware"}, \
            status.HTTP_500_INTERNAL_SERVER_ERROR

    return {"firmware": "successfully deployed"},\
        status.HTTP_201_CREATED


@bp.route('/local_config', methods=['PUT'])
def deploy_local_config():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy': 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    chip_id = request.headers.get("X-chip-id")
    if not chip_id:
        return {'local_config': 'no CHIP ID given'}, status.HTTP_404_NOT_FOUND

    local_conf = None
    config_file = os.path.join(current_app.instance_path,
                               "config.json.%s" % (chip_id))
    try:
        with open(config_file, "rb") as f:
            local_conf = f.read()
    except OSError:
        local_conf = b"{'config_version': 0}"

    try:
        j = json.loads(local_conf)
    except json.JSONDecodeError:
        j = {'config_version': 0}

    if "config_version" not in j.keys():
        j = {'config_version': 0}

    new_config = request.get_json()
    if not isinstance(new_config, dict):
        return {'local_config': 'invalid config'}, status.HTTP_400_BAD_REQUEST
    new_config["config_version"] = int(j["config_version"]) + 1

    try:
        with open(config_file, "w") as f:
            json.dump(new_config, f, indent=4)
    except OSError as eos:
        print(eos)
        return {'local_config': 'failed to write config'}, \
            status.HTTP_500_INTERNAL_SERVER_ERROR

    return {'local_config': 'successfully deployed'}, status.HTTP_201_CREATED


@bp.route('/global_config', methods=['PUT'])
def deploy_global_config():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy': 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    key = request.headers.get("X-global-config-key")
    if not key:
        return {'global_config': 'no key supplied'}, status.HTTP_403_FORBIDDEN

    key = base64.b64decode(key)
    if len(key) != 32:
        return {'global_config': 'invalid key'}, status.HTTP_403_FORBIDDEN

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
        global_conf = b"{'global_config_version': 0}"

    j = None
    try:
        j = json.loads(global_conf.decode("utf-8"))
    except json.JSONDecodeError:
        j = {'global_config_version': 0}

    new_config = request.get_json()
    if not isinstance(new_config, dict):
        return {'global_config': 'invalid config'}, status.HTTP_400_BAD_REQUEST
    new_config["global_config_version"] = int(j["global_config_version"]) + 1

    try:
        with open(config_file, "wb") as f:
            plaintext = json.dumps(new_config, indent=4).encode("utf-8")
            f.write(box.encrypt(plaintext))
    except OSError as eos:
        print(eos)
        return {'global_config': 'failed to write config'},\
            status.HTTP_500_INTERNAL_SERVER_ERROR

    return {'global_config': 'successfully deployed'}, status.HTTP_201_CREATED
