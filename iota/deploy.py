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

    return {}

@bp.route('/global_config', methods=['PUT'])
def deploy_global_config():
    token = request.headers.get("X-auth-token")
    if not verify(token, access="w"):
        return {'deploy' : 'not authorized'}, status.HTTP_401_UNAUTHORIZED

    return {}
