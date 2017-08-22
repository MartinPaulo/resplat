# This file shows the settings that can be placed in local_settings.py
# local_settings.py is a way for us to have machine specific information
# if (any)

# SECURITY WARNING: keep the secret key used in production secret!
# if lazy, use https://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = 'replace_me!'

# Debug defaults to False
DEBUG = False
# Hence the following allowed hosts will stop the server from running...
# So you need to set it to be whatever server the software is running on
ALLOWED_HOSTS = []

# These are the people that email will flow to...
ADMINS = (
    ('One Admin', 'one.admin@somewhere.edu.au'),
    ('Two Admin', 'two.admin@somewhere.edu.au')
)

MANAGERS = (
    ('One Manager', 'one.manager@somewhere.edu.au'),
    ('Two Manager', 'two.manager@somewhere.edu.au')
)

# enable and set if you don't want email to come from root@localhost
# SERVER_EMAIL = 'rc-melbourne@nectar.org.au'
# DEFAULT_FROM_EMAIL = 'rc-melbourne@nectar.org.au'

# enable and point to the static files location
# STATIC_ROOT = '/var/www/static'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'some_db_name',
        'USER': 'some_user',
        'PASSWORD': 'some_password',
        'HOST': 'some_host',
        'PORT': '5432',
    }
}

# Change these to be appropriate for the environment
ENVIRONMENT_NAME="Production"
ENVIRONMENT_COLOR="red"

# set to wherever you want your static files to live
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# STATIC_ROOT = '/var/www/static'

# If running in debug mode, this will connect to the python debugging server
# launched as follows:
# python -m smtpd -n -c DebuggingServer localhost:1025
# The debugging server will simply print all email sent by the application to
# the command line.
if DEBUG:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'debug@reporting.uom.edu.au'
