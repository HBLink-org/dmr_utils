#! /bin/bash

test -x ./setup.py || exit 1
apt-get install python-dev
pip install --upgrade .

