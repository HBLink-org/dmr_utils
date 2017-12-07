#! /bin/bash

# Install the required support programs
apt-get install unzip -y
apt-get install python-dev -y
apt-get install python-pip -y
apt-get install python-twisted -y

test -e ./setup.py || exit 1
pip install --upgrade .

