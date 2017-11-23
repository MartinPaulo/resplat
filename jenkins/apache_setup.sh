#!/bin/bash

cp jenkins/resplat.apache2.conf /etc/apache2/sites-available/
rm /etc/apache2/sites-enabled/000-default.conf
ln -s /etc/apache2/sites-available/resplat.apache2.conf /etc/apache2/sites-enabled/resplat.apache2.conf

systemctl restart apache2
