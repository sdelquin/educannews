#!/bin/bash

cd "$(dirname "$0")"
exec pipenv run python main.py
