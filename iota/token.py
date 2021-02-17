#
# (C) Copyright 2020 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
# original source from
#  https://flask.palletsprojects.com/en/1.1.x/tutorial/
#
import base64
import nacl.pwhash
import nacl.utils
import re
import sqlite3

from flask import (
    Blueprint,
    request,
)
from flask_api import status

from iota.db import get_db

bp = Blueprint('token', __name__, url_prefix='/api/v1')


def check_hash(token_name, token):
    if not token_name or not token or len(token_name) == 0 or len(token) < 32:
        return False

    db = get_db()
    result = db.execute("SELECT token FROM tokens WHERE name = ?",
                        (token_name,)).fetchone()

    if not result:
        return False

    try:
        pwhash = result["token"] if type(result["token"]) == "byte" else \
            result["token"].encode("utf-8")
        token = token if type(token) == "byte" else token.encode("utf-8")
        return nacl.pwhash.verify(pwhash, token)
    except nacl.exceptions.InvalidkeyError:
        return False


def verify(token, access="r"):
    if not token or len(token) < 32 or not access or len(access) < 1:
        return False

    db = get_db()
    result = db.execute("SELECT name, token FROM tokens WHERE \
                        permissions LIKE ? OR permissions LIKE '%%a%%'",
                        ("%%" + access + "%%",)).fetchall()

    if not result:
        return False

    token = token if type(token) == "byte" else token.encode("utf-8")
    for r in result:
        try:
            pwhash = r["token"] if type(r["token"]) == "byte" else \
                r["token"].encode("utf-8")
            return nacl.pwhash.verify(pwhash, token)
        except nacl.exceptions.InvalidkeyError:
            pass

    return False


def show_token(token_name=None):
    result = None
    db = get_db()
    if token_name:
        result = db.execute("SELECT name,permissions FROM tokens WHERE \
                            name = ?",
                            (token_name,)).fetchone()
    else:
        result = db.execute("SELECT name,permissions FROM tokens").fetchall()

    if not result:
        return {}, status.HTTP_404_NOT_FOUND

    return {"tokens": [{"name": r["name"], "permissions": r["permissions"]}
                       for r in result]}, status.HTTP_200_OK


def gen_token(nbytes=64):
    return base64.b64encode(nacl.utils.random(nbytes))


def new_token(token_name, token_perm):
    db = get_db()
    token = gen_token()
    token_perm = re.sub(r"[^arw]", "", token_perm)
    try:
        db.execute("INSERT INTO tokens (name, token, permissions) \
                    VALUES (?, ?, ?)",
                   (token_name, nacl.pwhash.str(token), token_perm,))
        db.commit()
    except sqlite3.Error as e:
        print(e)
        return {}, status.HTTP_409_CONFLICT

    return {"name": token_name,
            "token": token,
            "permissions": token_perm}, status.HTTP_201_CREATED


def update_token(token_name, token_perm, token_regen):
    db = get_db()
    if token_perm:
        token_perm = re.sub(r"[^arw]", "", token_perm)

    if token_regen and token_perm and len(token_perm) > 0:
        token = gen_token()
        try:
            db.execute("UPDATE tokens SET token = ?, permissions = ? \
                        WHERE name = ?",
                       (nacl.pwhash.str(token), token_perm, token_name,))
            db.commit()
        except sqlite3.Error as e:
            print(e)
            return {}, status.HTTP_400_BAD_REQUEST
    elif token_regen:
        token = gen_token()
        try:
            db.execute("UPDATE tokens SET token = ? WHERE name = ?",
                       (nacl.pwhash.str(token), token_name,))
            db.commit()
        except sqlite3.Error as e:
            print(e)
            return {}, status.HTTP_400_BAD_REQUEST
    elif token_perm and len(token_perm) > 0:
        try:
            db.execute("UPDATE tokens SET permissions = ? WHERE name = ?",
                       (token_perm, token_name,))
            db.commit()
        except sqlite3.Error as e:
            print(e)
            return {}, status.HTTP_400_BAD_REQUEST
    else:
        return {}, status.HTTP_400_BAD_REQUEST

    return {"name": token_name,
            "token": token if token_regen else "***",
            "permissions": token_perm if token_perm else "***"},\
        status.HTTP_200_OK


def delete_token(token_name):
    db = get_db()
    try:
        db.execute("DELETE FROM tokens WHERE name = ?",
                   (token_name,))
        db.commit()
    except sqlite3.Error as e:
        print(e)
        return {}, status.HTTP_400_BAD_REQUEST

    return {}, status.HTTP_202_ACCEPTED


@bp.route('/token', methods=['GET', 'PUT', 'UPDATE', 'DELETE'])
def token():
    token = request.headers.get("X-auth-token")
    if not verify(token, "r"):
        return {}, status.HTTP_403_FORBIDDEN

    content = request.get_json()
    token_name = None
    token_perm = None
    token_regen = False
    if content:
        if "name" in content.keys():
            token_name = content["name"]
        if "permissions" in content.keys():
            token_perm = content["permissions"]
        if "token" in content.keys():
            token_regen = True

    if request.method == "GET":
        if verify(token, "a"):
            return show_token(token_name)
        if check_hash(token_name, token):
            return show_token()
    elif request.method == "PUT":
        if verify(token, "a") and token_name and token_perm:
            return new_token(token_name, token_perm)
    elif request.method == "UPDATE":
        if verify(token, "a") and token_name and (token_perm or token_regen):
            return update_token(token_name, token_perm, token_regen)
    elif request.method == "DELETE":
        if verify(token, "a") and token_name:
            return delete_token(token_name)
    else:
        return {}, status.HTTP_404_NOT_FOUND

    return {}, status.HTTP_404_NOT_FOUND
