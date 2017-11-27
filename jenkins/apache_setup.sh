#!/bin/bash
#
# Setup apache2 on this server for just this application
#
# Arguments:
#   None

cp jenkins/resplat.apache2.conf /etc/apache2/sites-available/
rm /etc/apache2/sites-enabled/000-default.conf
ln -s /etc/apache2/sites-available/resplat.apache2.conf /etc/apache2/sites-enabled/resplat.apache2.conf

systemctl restart apache2
