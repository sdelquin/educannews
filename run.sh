#!/bin/bash

source ~/.pyenv/versions/educannews/bin/activate
cd "$(dirname "$0")"
exec python main.py notify
