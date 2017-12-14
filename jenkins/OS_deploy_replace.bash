#!/bin/bash
#
# OpenStack deployment of the application server via HEAT & replaces previous stack(s) if successful
#

set +x


### Parameter setup & check
if [ -z "$1" ]; then
    echo "Usage: ./OS_deploy_replace.bash (profile)"
    echo "  profile: A shell script with environment variables this script needs. Make a copy of example.profile.template and fill in the details"
    exit
fi
source "$1"

_params=($(cat <<EOF
OS_AUTH_URL
OS_PROJECT_NAME
OS_USERNAME
OS_PASSWORD
STACK_PREFIX
STACK_KEY
STACK_IMAGE_ID
STACK_FLAVOR_ID
STACK_SECURITY_GROUP_ID
SCRIPT_HOME
LOCAL_SETTINGS_PY_SRC
EXTRA_SSH_KEYS
WEB_FRONT_USER
WEB_FRONT_IP
WAIT_CHECK_SECONDS
EOF
))

# Scan for each environment variable in _params list
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


### Util functions
_err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] ERROR: $@" >&2
}
_info() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] INFO: $@"
}
_exitIfError() {
    if [ $? -ne 0 ]; then
        _err $1
        exit 1
    fi
}



### Deployment
_info "Analysing current stack status"

stacks=($(openstack stack list -c "Stack Name" -f value | grep $STACK_PREFIX))
_exitIfError "Failed to fetch previous stack lists"

# Find the last number and increment for new name
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

# Copy local files to relative folder for deploy.yaml to process (temporary)
cp "$LOCAL_SETTINGS_PY_SRC" "$SCRIPT_HOME/local_settings.py"
cp "$EXTRA_SSH_KEYS" "$SCRIPT_HOME/extra_ssh_keys.pub"

# HEAT
_info "Starting HEAT deployment"

TIME_START=$SECONDS
openstack stack create -t "$SCRIPT_HOME/deploy.yaml" \
    --parameter key_name="$STACK_KEY" \
    --parameter image_id="$STACK_IMAGE_ID" \
    --parameter instance_type="$STACK_FLAVOR_ID" \
    --parameter web_front_sec_id="$STACK_SECURITY_GROUP_ID" \
    "$NEW_NAME"
_exitIfError "Stack create command failed."

# Clean up copied files
rm "$SCRIPT_HOME/local_settings.py"
rm "$SCRIPT_HOME/extra_ssh_keys.pub"

# Wait for HEAT complete
is_successful=0
while [[ 1 ]]; do
    stack_status=$(openstack stack show "$NEW_NAME" -c stack_status -f value)
    _exitIfError "Failed to get stack deployment status"

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
    _info "$(($TIME_DIFF / 60)) minutes and $(($TIME_DIFF % 60)) seconds elapsed. Stack Status: $stack_status"
    sleep $WAIT_CHECK_SECONDS
done

# Check success
if [ "$is_successful" = "0" ]; then
    _err "Stack creation unsuccessful. Previous stack untouched."
    exit 1
fi


### Post deploy setup
_info "Setting up new proxy pass"

NEW_IP=$(openstack stack output show $NEW_NAME instance_ip -c output_value -f value)
_exitIfError "Failed to get IP address of new server"
_info "$NEW_NAME IP address is $NEW_IP"

# Update the proxy on WEB_FRONT server over ssh
WEB_FRONT_SSH_C="ssh $WEB_FRONT_USER@$WEB_FRONT_IP ./change_proxy.sh "
$WEB_FRONT_SSH_C "$NEW_IP"
_exitIfError "Failed to update IP address on WEB_FRONT using command: $WEB_FRONT_SSH_C $NEW_IP"
_info "WEB_FRONT server updated."



### Delete all old stacks method
_info "Stack cleanup stage"

for stack in "${stacks[@]}"; do
    _info "Deleting old stack $stack"
    openstack stack delete -y "$stack"
    _exitIfError "Failed to delete stack: $stack. Exiting. Review stack list"
done



_info "Script complete."
_info "================"
_info "New Application server: $NEW_IP"
_info "================"



