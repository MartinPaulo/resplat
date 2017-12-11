#!/bin/sh

# Password to decrypt gpg file
export DB_KEY=""
# URL to fetch the encrypted tgz of an pg_dump
export DB_OBJECT_URL="https://swift.rc.nectar.org.au:8888/v1/...sql.tgz.gpg"

# If using 'existing' mode, this is the name/ip of the instance to talk to
# If using 'heat' mode, this will be overwritten by the IP address of the new instance
export DB_HOST="postgres"

# If using 'existing' mode, password for postgres user
# If using 'heat' mode, this sets the password for postgres user
export PGPASSWORD=""

# Other database connection settings. These will be written to local_settings.py for you
export DB_NAME="vicnode_db"
export DB_USER="vicnode_prd"
export DB_PASSWORD=""


# Specific a new Django admin user.
export SU_NAME="vicnode_admin"
export SU_EMAIL=""
export SU_PASSWORD=""


# Name of Heat stack
export OS_STACK_NAME="teststackdb_1"
# Trove db.small, use 'trove flavor-list'
export TROVE_FLAVOR="325c919d-b523-4960-968c-f2baffafff94"
# In GB
export TROVE_SIZE="1"
# PostgreSQL, use 'datastore-list'
export TROVE_STORE_ID="95d6a64a-dd83-4e3b-b843-0c41754ac4ee"



# Source a openstack rc profile
. ~/Resplat-Reporting-openrc.sh
