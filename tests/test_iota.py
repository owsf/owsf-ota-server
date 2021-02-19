#
# (C) Copyright 2021 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
import json
import os

TEST_ADMIN_TOKEN = \
    "QWw6kjrJY5xB4VSzWns+DZjM7Tda5CI9YlEmq43oTsQAeTHJpuG+gc4ZVr21hs+XkcXo5IQGix\
KV+QhUKhTdeA=="
TEST_READER_TOKEN = \
    "UbIwkJJ8ranX9FWcnALyAfq3du5dPG+CfNhjA++O+gjl+WQnonp4wSAavxwWt/48LlET+Eowvb\
D9cbXgTT3Q2w=="
TEST_WRITER_TOKEN = \
    "YOEN2RhX5kyMx+f/v1Jpg5B4p+R9u+XAvy9zP2x6yB7NkdutedlI++QMJpQ6qDOoyUW/PkpvY7\
lhLpe8yA1nRQ=="


def test_token_get(client):
    headers = {
        "X-auth-token": "INVALID BUT REALY LONG TOKEN FOR TESTING",
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply.status_code == 403

    headers = {
        "X-auth-token": TEST_READER_TOKEN,
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply.status_code == 404

    headers = {
        "X-auth-token": TEST_READER_TOKEN,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "name": "reader"
    })
    reply = client.get('/api/v1/token', headers=headers, data=data)
    assert reply.status_code == 200
    assert b"reader" in reply.data

    headers = {
        "X-auth-token": TEST_ADMIN_TOKEN,
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply.status_code == 200
    assert b"reader" in reply.data
    assert b"writer" in reply.data
    assert b"admin" in reply.data


def test_token_put(client):
    headers = {
        "X-auth-token": TEST_READER_TOKEN,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "name": "test1",
        "permissions": "arw",
    })
    reply = client.put('/api/v1/token', headers=headers, data=data)
    assert reply.status_code == 404

    headers = {
        "X-auth-token": TEST_WRITER_TOKEN,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "name": "test1",
        "permissions": "arw",
    })
    reply = client.put('/api/v1/token', headers=headers, data=data)
    assert reply.status_code == 404

    headers = {
        "X-auth-token": TEST_ADMIN_TOKEN,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "name": "test_token",
        "permissions": "r",
    })
    reply = client.put('/api/v1/token', headers=headers, data=data)
    assert reply.status_code == 201

    headers = {
        "X-auth-token": TEST_ADMIN_TOKEN,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "name": "test_token",
        "permissions": "r",
    })
    reply = client.put('/api/v1/token',
                       headers=headers, data=data)
    assert reply.status_code == 409

    headers = {
        "X-auth-token": TEST_ADMIN_TOKEN,
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply.status_code == 200
    assert b"test_token" in reply.data


# TODO client has no update() function
# implement update() function and the /api/v1/token UPDATE tests

def test_token_delete(client):
    headers = {
        "X-auth-token": TEST_ADMIN_TOKEN,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "name": "test_token",
        "permissions": "r",
    })
    reply = client.put('/api/v1/token', headers=headers, data=data)
    assert reply.status_code == 201

    reply = client.delete('/api/v1/token', headers=headers, data=data)
    assert reply.status_code == 202

    headers = {
        "X-auth-token": TEST_ADMIN_TOKEN,
    }
    reply = client.get('/api/v1/token', headers=headers)
    assert reply.status_code == 200
    assert b"test_token" not in reply.data


def test_deploy_local_config(client, app):
    local_config_file = os.path.join(os.path.dirname(__file__), "..",
                                     "instance", "config.json.0x00000001")
    if os.path.exists(local_config_file):
        os.unlink(local_config_file)

    headers = {
        "X-auth-token": TEST_WRITER_TOKEN,
        "Content-Type": "application/json",
        "X-chip-id": "0x00000001",
    }
    data = json.dumps({
        "config_version": 1,
        "name": "test sensor"
    })
    reply = client.put('/api/v1/deploy/local_config',
                       headers=headers, data=data)
    assert reply.status_code == 201
    assert b"successfully" in reply.data

    reply = client.put('/api/v1/deploy/local_config',
                       headers=headers, data=data)
    assert reply.status_code == 304
    os.unlink(local_config_file)


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
