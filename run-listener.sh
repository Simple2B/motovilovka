#!/usr/bin/env bash
echo wait 20 seconds for starting MQTT broker
sleep 20
poetry run flask db upgrade
echo start server
flask mqtt
