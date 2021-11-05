#!/bin/bash

source ~/.virtualenvs/educannews/bin/activate
cd "$(dirname "$0")"
git pull
pip install -r requirements.txt
