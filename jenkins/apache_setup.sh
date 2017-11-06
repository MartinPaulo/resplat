#!/bin/bash

set -x

# Enable apache2 SSL
a2enmod ssl

# Generate Self signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/certs/resplat.key -out /etc/ssl/certs/resplat.crt <<EOF
AU
Victoria
Melbourne
The University of Melbourne


 
EOF


# Make apache2 site configuration file
cat <<EOF > /etc/apache2/sites-available/resplat.apache2.conf
<VirtualHost *:443>
   SSLEngine on
   SSLCertificateFile /etc/ssl/certs/resplat.crt
   SSLCertificateKeyFile /etc/ssl/certs/resplat.key

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


#service apache2 restart
