#!/bin/bash

set -x


cat <<EOF > /etc/apache2/sites-available/resplat.apache2.conf
<VirtualHost *:80>
   Alias /static /var/www/static
   <Directory /var/www/static>
      Require all granted
   </Directory>
   <Directory /resplat/resplat>
      <Files wsgi.py>
         Require all granted
      </Files>
   </Directory>
   WSGIDaemonProcess resplat python-home=/usr/bin/python3 python-path=/resplat
   WSGIProcessGroup resplat
   WSGIScriptAlias / /resplat/resplat/wsgi.py
</VirtualHost>
EOF
rm /etc/apache2/sites-enabled/000-default.conf
ln -s /etc/apache2/sites-available/resplat.apache2.conf /etc/apache2/sites-enabled/resplat.apache2.conf

service apache2 restart
