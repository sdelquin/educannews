#!/bin/bash

source ~/.virtualenvs/educannews/bin/activate
cd "$(dirname "$0")"
exec python main.py notify
