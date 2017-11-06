#!/bin/bash

apt-get update
#apt-get upgrade
apt-get install -y python3-pip python3-dev python3-tk apache2 libapache2-mod-wsgi-py3
apt-get install -y postgresql postgresql-contrib
apt-get install -y git curl libpq-dev
apt-get install -y sudo
apt-get install -y vim
ln -fs /usr/bin/python3 /usr/bin/python
pip3 install --upgrade pip
pip install -r requirements.txt
python3 manage.py collectstatic --no-input
