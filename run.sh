#!/bin/bash

source ~/.virtualenvs/educannews/bin/activate
cd "$(dirname "$0")"
exec python educannews.py notify
