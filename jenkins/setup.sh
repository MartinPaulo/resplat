#!/bin/bash
#
# Installs all operating system software dependencies including apt-get and pip installs
# Setup apache2 on this server for just this application
#
# Arguments:
#   None

set -x

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

cp jenkins/resplat.apache2.conf /etc/apache2/sites-available/
rm /etc/apache2/sites-enabled/000-default.conf
ln -s /etc/apache2/sites-available/resplat.apache2.conf /etc/apache2/sites-enabled/resplat.apache2.conf

