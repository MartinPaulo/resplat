#!/bin/bash

set +x

assertArg() {
    if [ -z "$2" ]; then
        echo "$1 is not set. Exiting"
		exit 1
    else
        echo "$1 is set to $2"
    fi
}
echoHeading () {
	echo "====="
	echo "$1"
	echo "====="
}
exitIfError() {
	if [ $? -ne 0 ]; then
		echo "FATAL ERROR: $1"
		exit 1
	fi
}


echoHeading "Checking arguments"
assertArg DB_KEY $DB_KEY
assertArg DB_NAME $DB_NAME
#assertArg DB_USER $DB_USER
DB_USER="vicnode_prd"
assertArg DB_PASSWORD $DB_PASSWORD
assertArg DB_HOST $DB_HOST
assertArg SU_NAME $SU_NAME
assertArg SU_EMAIL $SU_EMAIL
assertArg SU_PASSWORD $SU_PASSWORD

if [ -z "$DB_OBJECT_URL" ]; then 
	DB_OBJECT_URL="https://swift.rc.nectar.org.au:8888/v1/AUTH_612a4df9bfab47c38324ead4e5f8dd79/trial/dump.sql.tgz.gpg"
fi
echo "DB_OBJECT_URL is set to: $DB_OBJECT_URL"

if [ -z "$PSQL" ]; then
	PSQL="sudo -u postgres psql"
fi
echo "PSQL command is: $PSQL"

if [ -z "$DEBUG" ]; then
        DEBUG="False"
fi
echo "DEBUG is: $DEBUG"

if [ -z "$ALLOWED_HOSTS" ]; then
        ALLOWED_HOSTS="\['\*'\]"
fi
echo "ALLOWED_HOSTS is: $ALLOWED_HOSTS"

if [ -z "$NEW_KEY" ]; then
        NEW_KEY=$(strings /dev/urandom | grep -o '[[:alnum:]]' | head -n 30 | tr -d '\n'; echo)
fi
echo "NEW_KEY is: $NEW_KEY"


echoHeading "Downloading, decrypting, extracting..."
curl -o data.sql.tgz.gpg ${DB_OBJECT_URL}
echo "$DB_KEY" | gpg --no-tty --decrypt --passphrase-fd 0 data.sql.tgz.gpg > data.sql.tgz
tar -zxvf data.sql.tgz
exitIfError "Failed to complete extraction process"


echoHeading "Creating Database"
$PSQL -c "CREATE DATABASE $DB_NAME TEMPLATE template0;"
exitIfError "Failed to create database"

echoHeading "Creating users and privileges"
$PSQL -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to $DB_USER;"
$PSQL -c "GRANT CREATE ON DATABASE $DB_NAME to $DB_USER;"

$PSQL -c "CREATE USER vicnode WITH PASSWORD '$DB_PASSWORD';"
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to vicnode;"
#$PSQL -c "GRANT CREATE ON DATABASE $DB_NAME to vicnode;"

$PSQL -c "CREATE USER vicnode_prd_ro WITH PASSWORD '$DB_PASSWORD';"
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to vicnode_prd_ro;"
#$PSQL -c "GRANT CREATE ON DATABASE $DB_NAME to vicnode_prd_ro;"


echoHeading "Loading data & fixing schema"
$PSQL $DB_NAME < my_vicnode_dump.sql > load_log.txt
exitIfError "Failed to load dump data"
$PSQL -d $DB_NAME -a -f DB_Scripts/db_transform.sql > transform_log.txt
exitIfError "Failed to apply db_transform.sql"




echoHeading "Creating Django local_settings.py"
cp resplat/local_settings_template.py resplat/local_settings.py
sed -i -e "s/'NAME'.*/'NAME': '$DB_NAME',/g" resplat/local_settings.py
sed -i -e "s/'USER'.*/'USER': '$DB_USER',/g" resplat/local_settings.py
sed -i -e "s/'PASSWORD'.*/'PASSWORD': '$DB_PASSWORD',/g" resplat/local_settings.py
sed -i -e "s/'HOST'.*/'HOST': '$DB_HOST',/g" resplat/local_settings.py
sed -i -e 's/DEBUG.*/DEBUG = '$DEBUG'/g' resplat/local_settings.py
sed -i -e "s/ALLOWED_HOSTS.*/ALLOWED_HOSTS = $ALLOWED_HOSTS/g" resplat/local_settings.py
sed -i -e "s/SECRET_KEY.*/SECRET_KEY='$NEW_KEY'/g" resplat/local_settings.py


echoHeading "Django migration"
python3 manage.py migrate --fake-initial
exitIfError "Failed to django migrate"

echoHeading "Creating initial admin user"
python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$SU_NAME', '$SU_EMAIL', '$SU_PASSWORD')"
exitIfError "Failed to make initial admin user"


