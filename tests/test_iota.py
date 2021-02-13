#
# (C) Copyright 2021 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
import json
import os
import tempfile

import pytest

ADMIN_TOKEN = \
    "QWw6kjrJY5xB4VSzWns+DZjM7Tda5CI9YlEmq43oTsQAeTHJpuG+gc4ZVr21hs+XkcXo5IQGixKV+QhUKhTdeA=="
READER_TOKEN = \
    "UbIwkJJ8ranX9FWcnALyAfq3du5dPG+CfNhjA++O+gjl+WQnonp4wSAavxwWt/48LlET+EowvbD9cbXgTT3Q2w=="
WRITER_TOKEN = \
    "YOEN2RhX5kyMx+f/v1Jpg5B4p+R9u+XAvy9zP2x6yB7NkdutedlI++QMJpQ6qDOoyUW/PkpvY7lhLpe8yA1nRQ=="


def test_token_get(client):
    headers = {
        "X-auth-token": "INVALID BUT REALY LONG TOKEN FOR TESTING",
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply == 403

    headers = {
        "X-auth-token": READER_TOKEN,
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply == 404

    headers = {
        "X-auth-token": READER_TOKEN,
    }
    data = json.dumps({
        "name": "reader"
    })
    reply = client.get('/api/v1/token', content_type="application/json", headers=headers, data=data)
    assert reply == 200
    assert b"reader" in reply.data

    headers = {
        "X-auth-token": ADMIN_TOKEN,
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply == 200
    assert b"reader" in reply.data


def test_token_put(client):
    pass


def test_token_update(client):
    pass


def test_token_delete(client):
    pass


def test_deploy_local_config(client):
    pass


def test_deploy_global_config(client):
    pass


def test_deploy_firmware(client):
    pass


def test_get_local_config(client):
    pass


def test_get_global_config(client):
    pass


def test_get_firmware(client):
    pass
