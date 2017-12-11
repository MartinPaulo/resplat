#!/bin/bash
#
# Boot strap a new Trove database with a legacy Vicnode Reporting database dump downloaded from a SWIFT store
# A new Trove database with a database will be created with a new random 'postgres' password
# A local_settings.py will be created
#
# Requires:
#   - A URL of where to find the PostgreSQL database dump from
#   - GPG decryption password
#   - New database connection values
#   - postgres user account for th database
#   - New django admin values
#   - Openstack tenancy with Trove quota and rc profile
# Set all of these in the environment before running script
# See example_environment.sh

set +x

_params=($(cat <<EOF
DB_OBJECT_URL
DB_KEY
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
PGPASSWORD
SU_NAME
SU_EMAIL
SU_PASSWORD
OS_AUTH_URL
OS_PROJECT_NAME
OS_USERNAME
OS_PASSWORD
OS_STACK_NAME
TROVE_FLAVOR
TROVE_SIZE
TROVE_STORE_ID
EOF
))

is_valid=true
for var in "${_params[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Missing environment variable $var"
        is_valid=false
    fi
done

if ! $is_valid; then
    echo "ERROR. Please ensure all variables are set"
    exit 1
fi

_err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] ERROR: $@" >&2
}
_info() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] INFO: $@"
}
exitIfError() {
	if [ $? -ne 0 ]; then
		_err $1
		exit 1
		fi
}

if ! [[ "$1" == "heat" || "$1" == "existing" ]] ; then
	echo "Usage: ./DB_Scripts/BootStrapDBFromLegacy.sh (heat|existing)"
	echo "  heat: Assumes OpenStack rc is loaded and will HEAT deploy a new Trove instance, to make a database on"
    echo "  existing: Assumes DB_HOST is an existing PostgreSQL instance and makes a database there"
	exit 1
fi




if [ -z "$NEW_KEY" ]; then
        NEW_KEY=$(strings /dev/urandom | grep -o '[[:alnum:]]' | head -n 30 | tr -d '\n'; echo)
fi
_info "Generated new Django key: $NEW_KEY"


_info "Downloading, decrypting, extracting..."
curl -o data.sql.tgz.gpg ${DB_OBJECT_URL}
echo "$DB_KEY" | gpg --no-tty --decrypt --passphrase-fd 0 data.sql.tgz.gpg > data.sql.tgz
tar -zxvf data.sql.tgz
sql_filename=$(tar -tzvf data.sql.tgz 2> /dev/null | grep -o '[^ ]*$')

exitIfError "Failed to complete extraction process"

if [ "$1" == "heat" ]; then
	_info "HEAT deploying new trove instance"
	TIME_START=$SECONDS
	openstack stack create -t DB_Scripts/deploy.yaml \
		--parameter instance_type="$TROVE_FLAVOR" \
		--parameter size_gb="$TROVE_SIZE" \
		--parameter store_id="$TROVE_STORE_ID" \
		"$OS_STACK_NAME"
	exitIfError "Failed to start stack creation"

	is_successful=0
	while [[ 1 ]]; do
		stack_status=$(openstack stack show "$OS_STACK_NAME" -c stack_status -f value)
		if [ "$stack_status" = "CREATE_COMPLETE" ]; then
			_info "Stack complete"
			is_successful=1
			break
		elif [ "$stack_status" = "CREATE_FAILED" ]; then
			_err "Stack creation failed"
			is_successful=0
			break
		fi
		TIME_DIFF=$(($SECONDS - $TIME_START))
		_info "$(($TIME_DIFF / 60)) minutes and $(($TIME_DIFF % 60)) seconds elapsed. stack_status: $stack_status"
		sleep 30
	done

	# Confirm success
	if [ "$is_successful" = "0" ]; then
		_err "Stack creation failed."
		exit 1
	fi


	DB_HOST=$(openstack stack output show "$OS_STACK_NAME" instance_ip -c output_value -f value)
	INSTANCE_NAME=$(openstack stack output show "$OS_STACK_NAME" instance_name -c output_value -f value)
	_info "New DB_HOST is $DB_HOST"
	_info "New INSTANCE_NAME is $INSTANCE_NAME"
	_info "Setting password for postgres user"
	trove root-enable --root_password="$PGPASSWORD" "$INSTANCE_NAME"
fi


PSQL="psql -h $DB_HOST -U postgres "

_info "Creating Database instance"
$PSQL -c "CREATE DATABASE $DB_NAME TEMPLATE template0;"
exitIfError "Failed to create database instance"

_info "Creating users and privileges"
$PSQL -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to $DB_USER;"
$PSQL -c "GRANT CREATE ON DATABASE $DB_NAME to $DB_USER;"

$PSQL -c "CREATE USER vicnode WITH PASSWORD '$DB_PASSWORD';"
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to vicnode;"
#$PSQL -c "GRANT CREATE ON DATABASE $DB_NAME to vicnode;"

$PSQL -c "CREATE USER vicnode_prd_ro WITH PASSWORD '$DB_PASSWORD';"
$PSQL -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME to vicnode_prd_ro;"
#$PSQL -c "GRANT CREATE ON DATABASE $DB_NAME to vicnode_prd_ro;"


_info "Loading data & fixing schema"
$PSQL $DB_NAME < $sql_filename > load_log.txt
exitIfError "Failed to load dump data"
$PSQL -d $DB_NAME -a -f DB_Scripts/db_transform.sql > transform_log.txt
exitIfError "Failed to apply db_transform.sql"



_info "Creating Django local_settings.py"
cp resplat/local_settings_template.py resplat/local_settings.py
sed -i -e "s/'NAME'.*/'NAME': '$DB_NAME',/g" resplat/local_settings.py
sed -i -e "s/'USER'.*/'USER': '$DB_USER',/g" resplat/local_settings.py
sed -i -e "s/'PASSWORD'.*/'PASSWORD': '$DB_PASSWORD',/g" resplat/local_settings.py
sed -i -e "s/'HOST'.*/'HOST': '$DB_HOST',/g" resplat/local_settings.py
sed -i -e 's/DEBUG.*/DEBUG = 'False'/g' resplat/local_settings.py
sed -i -e "s/ALLOWED_HOSTS.*/ALLOWED_HOSTS = \['\*'\]/g" resplat/local_settings.py
sed -i -e "s/SECRET_KEY.*/SECRET_KEY='$NEW_KEY'/g" resplat/local_settings.py


_info "Django migration"
python3 manage.py migrate --fake-initial
exitIfError "Failed to django migrate"

_info "Creating initial admin user"
python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$SU_NAME', '$SU_EMAIL', '$SU_PASSWORD')"
exitIfError "Failed to make initial admin user"


