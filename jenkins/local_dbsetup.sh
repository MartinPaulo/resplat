#!/bin/bash

set -x


service postgresql restart

# Download and extract
curl -o data.sql.tgz.gpg https://swift.rc.nectar.org.au:8888/v1/AUTH_612a4df9bfab47c38324ead4e5f8dd79/trial/dump.sql.tgz.gpg
echo "$DB_KEY" | gpg --no-tty --decrypt --passphrase-fd 0 data.sql.tgz.gpg > data.sql.tgz
tar -zxvf data.sql.tgz

# Make DB
DB_EXISTS_SQL="SELECT 1 FROM pg_database WHERE datname='$DB_NAME'"
DOES_DB_EXISTS=$(sudo -u postgres psql -tAc "$DB_EXISTS_SQL")
if [ "${DEV_BUILD}" = "true" ] && [ "x$DOES_DB_EXISTS" = "x1" ]; then
	sudo -u postgres psql -c "DROP DATABASE $DB_NAME;"
fi
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

DB_SETUP_SQL="""
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to $DB_USER;
GRANT create ON DATABASE $DB_NAME to $DB_USER;

CREATE USER vicnode WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to vicnode;
GRANT create ON DATABASE $DB_NAME to vicnode;

CREATE USER vicnode_prd_ro WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to vicnode_prd_ro;
GRANT create ON DATABASE $DB_NAME to vicnode_prd_ro;

ALTER ROLE vicnode_prd CREATEDB;
"""

## Needs PGPASSWORD in env for following:
sudo -u postgres psql -c "$DB_SETUP_SQL"
sudo -u postgres psql $DB_NAME < my_vicnode_dump.sql > load_log.txt
sudo -u postgres psql -d $DB_NAME -a -f heat/db_transform.sql > transform_log.txt

