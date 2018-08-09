#!/bin/bash

cd "$(dirname "$0")"
source $(pipenv --venv)/bin/activate
exec python main.py
