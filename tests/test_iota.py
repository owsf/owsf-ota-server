#
# (C) Copyright 2021 Tillmann Heidsieck
#
# SPDX-License-Identifier: MIT
#
import base64
import json
import nacl.utils
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
TEST_GLOBAL_CONFIG_KEY = \
    "CdBVIMvt5R5sX0lPY2pkVUvVyVAEPoHV4SjqI4qmDss="
TEST_FIRMWARE_LENGTH = 512
TEST_FIRMWARE_DATA = base64.b64encode(nacl.utils.random(TEST_FIRMWARE_LENGTH))


def upload_firmware(client, version="v1.0", data=TEST_FIRMWARE_DATA):
    headers = {
        "X-auth-token": TEST_WRITER_TOKEN,
        "X-firmware-version": version,
        "Content-Type": "text/plain",
    }
    return client.put('/api/v1/deploy/firmware', headers=headers, data=data)


def upload_global_config(client, version=1):
    hdrs = {
        "X-auth-token": TEST_WRITER_TOKEN,
        "X-global-config-key": TEST_GLOBAL_CONFIG_KEY,
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "global_config_version": version,
    })
    return client.put('/api/v1/deploy/global_config', headers=hdrs, data=data)


def upload_local_config(client, version=1, chip_id="0x00000001"):
    hdrs = {
        "X-auth-token": TEST_WRITER_TOKEN,
        "Content-Type": "application/json",
        "X-chip-id": chip_id,
    }
    dat = json.dumps({
        "name": "test sensor"
    })

    return client.put('/api/v1/deploy/local_config', headers=hdrs, data=dat)


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

    reply = upload_local_config(client)
    assert reply.status_code == 201
    assert b"successfully" in reply.data

    os.unlink(local_config_file)


def test_deploy_global_config(client):
    global_config_file = os.path.join(os.path.dirname(__file__), "..",
                                      "instance", "global_config.enc")
    if os.path.exists(global_config_file):
        os.unlink(global_config_file)

    reply = upload_global_config(client)
    assert reply.status_code == 201
    assert b"successfully" in reply.data

    os.unlink(global_config_file)


def test_deploy_firmware(client):
    firmware_sig_file = os.path.join(os.path.dirname(__file__), "..",
                                     "instance", "firmware.sig")
    firmware_json_file = os.path.join(os.path.dirname(__file__), "..",
                                      "instance", "firmware.json")
    if os.path.exists(firmware_sig_file):
        os.unlink(firmware_sig_file)
    if os.path.exists(firmware_json_file):
        os.unlink(firmware_json_file)

    reply = upload_firmware(client)
    assert reply.status_code == 201
    assert b"successfully" in reply.data

    with open(firmware_sig_file, "rb") as f:
        firmware = f.read()

    assert len(firmware) == TEST_FIRMWARE_LENGTH
    assert base64.b64encode(firmware) == TEST_FIRMWARE_DATA

    os.unlink(firmware_sig_file)
    os.unlink(firmware_json_file)


def test_get_local_config(client):
    local_config_file = os.path.join(os.path.dirname(__file__), "..",
                                     "instance", "config.json.0x00000001")

    try:
        os.unlink(local_config_file)
    except OSError:
        pass

    upload_local_config(client, version=1, chip_id="0x00000001")

    hdrs = {
        "X-chip-id": "0x00000001",
        "X-config-version": 0,
    }
    reply = client.get('/api/v1/local_config', headers=hdrs)
    assert reply.status_code == 200
    resp = json.loads(reply.data.decode('utf8'))
    assert resp["config_version"] == 1

    try:
        os.unlink(local_config_file)
    except OSError:
        pass


def test_get_global_config(client):
    global_config_file = os.path.join(os.path.dirname(__file__), "..",
                                      "instance", "global_config.enc")

    upload_global_config(client)

    hdrs = {
        "X-global-config-version": 0,
        "X-global-config-key": TEST_GLOBAL_CONFIG_KEY,
    }
    reply = client.get('/api/v1/global_config', headers=hdrs)
    assert reply.status_code == 200
    resp = json.loads(reply.data.decode('utf-8'))
    assert resp["global_config_version"] == 1

    try:
        os.unlink(global_config_file)
    except OSError:
        pass


def test_get_firmware(client):
    firmware_sig_file = os.path.join(os.path.dirname(__file__), "..",
                                     "instance", "firmware.sig")
    firmware_json_file = os.path.join(os.path.dirname(__file__), "..",
                                      "instance", "firmware.json")
    upload_firmware(client, data=TEST_FIRMWARE_DATA)
    hdrs = {
        'X-ESP8266-version': 'v0.1',
    }
    reply = client.get('/api/v1/firmware', headers=hdrs)
    assert reply.status_code == 200
    assert len(reply.data) == TEST_FIRMWARE_LENGTH
    assert base64.b64encode(reply.data) == TEST_FIRMWARE_DATA
    try:
        os.unlink(firmware_sig_file)
        os.unlink(firmware_json_file)
    except OSError:
        pass
