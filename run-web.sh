#!/usr/bin/env bash
echo sleep 5
flask db upgrade
echo sleep 5
flask run --host=0.0.0.0 --port=80
