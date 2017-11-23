#!/bin/bash

set +x

# Enable apache2 SSL
#a2enmod ssl

# Generate Self signed certificate
#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/certs/resplat.key -out /etc/ssl/certs/resplat.crt <<EOF
#AU
#Victoria
#Melbourne
#The University of Melbourne
#
#
# 
#EOF


cp jenkins/resplat.apache2.conf /etc/apache2/sites-available/
rm /etc/apache2/sites-enabled/000-default.conf
ln -s /etc/apache2/sites-available/resplat.apache2.conf /etc/apache2/sites-enabled/resplat.apache2.conf


#service apache2 restart
systemctl restart apache2
