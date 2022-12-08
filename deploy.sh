#!/bin/bash

source ~/.pyenv/versions/educannews/bin/activate
cd "$(dirname "$0")"
git pull
pip install -r requirements.txt
