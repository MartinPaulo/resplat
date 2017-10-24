#!/bin/bash

set -x


cp resplat/local_settings_template.py resplat/local_settings.py
# Ok: Don't run in debug mode...
sed -i -e 's/DEBUG = True/DEBUG = False/g' resplat/settings.py
# Let Django know about the host
sed -i -e "s/ALLOWED_HOSTS = \[]/ALLOWED_HOSTS = \['\*']/g" resplat/settings.py
sed -i -e "s/SECRET_KEY.*/SECRET_KEY='NEW_KEY'/g" resplat/settings.py

sed -i -e "s/'NAME'.*/'NAME': '$DB_NAME',/g" resplat/local_settings.py
sed -i -e "s/'USER'.*/'USER': '$DB_USER',/g" resplat/local_settings.py
sed -i -e "s/'PASSWORD'.*/'PASSWORD': '$DB_PASSWORD',/g" resplat/local_settings.py
sed -i -e "s/'HOST'.*/'HOST': '$DB_HOST',/g" resplat/local_settings.py

python3 manage.py migrate --fake-initial
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('$SU_NAME', '$SU_EMAIL', '$SU_PASSWORD')" | python3 manage.py shell -c
python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$SU_NAME', '$SU_EMAIL', '$SU_PASSWORD')"
python3 manage.py collectstatic --no-input

