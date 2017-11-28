#!/bin/sh
#
# OpenStack deployment via HEAT & replaces previous stack if successful
#
# Arguments:
#   .

set +x

SCRIPT_HOME=/Users/loa1/Documents/Git/resplat/jenkins
STACK_PREFIX=resplat_auto_
LOCAL_SETTINGS_PY_SRC=/Users/loa1/resplat_local_settings.py
ENVIRONMENT_YAML=/Users/loa1/Documents/Git/resplat/jenkins/environment.yaml
WAIT_CHECK_SECONDS=30
WEB_FRONT_SSH_C="ssh ubuntu@115.146.84.124 ./change_proxy.sh "

_params=($(cat <<EOF
SCRIPT_HOME
STACK_PREFIX
LOCAL_SETTINGS_PY_SRC
ENVIRONMENT_YAML
WAIT_CHECK_SECONDS
OS_AUTH_URL
OS_PROJECT_NAME
OS_USERNAME
OS_PASSWORD
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


# Get envvars
#if [ -z "$2" ]; then
#	echo "Usage: bash OS_deploy_replace.bash (profile) (change ip: true|false)"
#fi



# Get previous name
_info "Analysing current stack status"
stacks=($(openstack stack list -c "Stack Name" -f value | grep $STACK_PREFIX))

highest=0
OLD_NAME=""
for stack in "${stacks[@]}"; do
	num=$(echo $stack | sed "s/^$STACK_PREFIX//")
	if [ "$num" -gt "$highest" ]; then
		highest=$num
		OLD_NAME=$stack
	fi
done
highest=$((highest +1))

NEW_NAME="$STACK_PREFIX$highest"

if [ "$OLD_NAME" = "" ]; then
	_info "No previous stack found. Starting new numbering"
else
	_info "Last stack found: $OLD_NAME"
fi

_info "New stack name will be: $NEW_NAME"

# HEAT
cp "$LOCAL_SETTINGS_PY_SRC" "$SCRIPT_HOME/local_settings.py"
TIME_START=$SECONDS
openstack stack create -t "$SCRIPT_HOME/deploy.yaml" -e "$ENVIRONMENT_YAML" "$NEW_NAME"

# Wait for HEAT complete
is_successful=0
while [[ 1 ]]; do
	stack_status=$(openstack stack show "$NEW_NAME" -c stack_status -f value)
	if [ "$stack_status" = "CREATE_COMPLETE" ]; then
		_info "Stack complete"
		is_successful=1
		break
	#else
	fi
	TIME_DIFF=$(($SECONDS - $TIME_START))
	_info "$(($TIME_DIFF / 60)) minutes and $(($TIME_DIFF % 60)) seconds elapsed. Still waiting..."
	sleep $WAIT_CHECK_SECONDS
done

# Confirm success
if [ "$is_successful" = "0" ]; then
	_err "Stack creation unsuccessful. Previous stack untouched."
	exit 1
	# TODO: If this happens in succession, there will be many stacks that increment. Someone manually needs to come clean up"
fi

NEW_IP=$(openstack stack output show $NEW_NAME instance_ip -c output_value -f value)
_info "$NEW_NAME IP address is $NEW_IP"

# Change ip addresss (cond)
$WEB_FRONT_SSH_C "$NEW_IP"
if [ !$? ]; then
	_err "Failed to update IP address on WEB_FRONT using command: $WEB_FRONT_SSH_C"
	exit 1
fi



# Delete old stack
if [ "$OLD_NAME" != "" ]; then
	_info "Deleting old stack $OLD_NAME"
	openstack stack delete -y "$OLD_NAME"
fi






