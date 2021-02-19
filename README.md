# esp8266-control-server

![Github Badge](https://github.com/junkdna/esp8266-control-server/workflows/Test%20and%20Lint/badge.svg) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/520536686d3d48adbcd59f4abc478399)](https://app.codacy.com/gh/junkdna/esp8266-control-server?utm_source=github.com&utm_medium=referral&utm_content=junkdna/esp8266-control-server&utm_campaign=Badge_Grade)

An OTA server for IOT devices. Currently designed to work in concert with the
corresponding the [ESP8266 firmware](https://github.com/junkdna/esp8266-sensor-firmware).

## Initialisation
A default token named `admin` with the value `QWw6kjrJY5xB4VSzWns+DZjM7Tda5CI9YlEmq43oTsQAeTHJpuG+gc4ZVr21hs+XkcXo5IQGixKV+QhUKhTdeA==`
is created on `flask init-db`.

In order to change the token use the API
```bash
curl -X UPDATE \
    -H "X-auth-token: QWw6kjrJY5xB4VSzWns+DZjM7Tda5CI9YlEmq43oTsQAeTHJpuG+gc4ZVr21hs+XkcXo5IQGixKV+QhUKhTdeA=="
    -H "Content-Type: application/json" -d '{"name": "admin", "token": "NEW_TOKEN"}' "$IOTA_URL/api/v1/token"
```
The server will create a new token and return it.

## Run the Server in a Container
Use the the [IOTA](https://github.com/junkdna/docker_iota) image.
