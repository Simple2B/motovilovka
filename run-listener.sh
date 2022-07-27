#!/usr/bin/env bash
sleep 5
poetry run flask db upgrade
sleep 5
echo start server
flask mqtt
