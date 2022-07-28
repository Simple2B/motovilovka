#!/usr/bin/env bash
echo wait 20 seconds for starting MQTT broker
sleep 20
flask db upgrade
flask run --host=0.0.0.0 --port=80
