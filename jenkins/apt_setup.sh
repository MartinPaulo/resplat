#!/bin/bash

apt-get update
apt-get upgrade
apt-get install -y python3-pip python3-dev python3-tk 
apt-get install -y apache2 libapache2-mod-wsgi-py3
apt-get install -y postgresql postgresql-contrib
apt-get install -y git curl libpq-dev
apt-get install -y sudo
apt-get install -y vim
pip3 install --upgrade pip
pip install -r requirements.txt
python3 manage.py collectstatic --no-input
