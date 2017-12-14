#!/bin/bash
#
# OpenStack deployment via HEAT for Web Front server.
#
# Arguments:
# - $1: Name of openstack stack
# - $2: Environment file
#

set +x


### Constants
WAIT_CHECK_SECONDS=30


### Parameter setup & check
if [ -z "$1" ]; then
    echo "Usage: ./OS_deploy_web_front.bash (stackname) (environmentfile)"
    echo "  stackname: Name of OpenStack stack"
    echo "  environmentfile: (Optional) Environment yaml file to use. Defaults to environment.yaml"
    exit
fi
STACK_NAME="$1"

if [ -z "$2" ]; then
    ENVIRONMENT_YAML="environment.yaml"
else
    ENVIRONMENT_YAML="$2"    
fi


### Util functions
_info() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] INFO: $@"
}
_err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] ERROR: $@" >&2
}
_exitIfError() {
    if [ $? -ne 0 ]; then
        _err $1
        exit 1
    fi
}


### Deployment
_info "Starting HEAT deployment"

TIME_START=$SECONDS
openstack stack create -t deploy_web_front.yaml -e "$ENVIRONMENT_YAML" "$STACK_NAME"
_exitIfError "Stack create command failed"

# Wait for HEAT to complete
is_successful=0
while [[ 1 ]]; do
    stack_status=$(openstack stack show "$STACK_NAME" -c stack_status -f value)
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
    exit 1
fi
_info "Stack creation successful."


### Post deploy setup
_info "Setting up http_only_security_group"

ip=$(openstack stack output show $STACK_NAME instance_ip -c output_value -f value)
_exitIfError "Failed to get IP address of new server"
_info "$STACK_NAME IP address is $ip"

sec_group_id=$(openstack stack resource list -c physical_resource_id -f value --filter name=http_only_security_group $STACK_NAME)
_exitIfError "Failed to get http_only_security_group ID"
_info "http_only_security_group: $sec_group_id"

openstack security group rule create --ingress --remote-ip "$ip/32" --dst-port "80:80" "$sec_group_id"
_exitIfError "Failed to create security group rule"


_info "Script complete."
_info "================"
_info "New Web Front server: $ip"
_info "http_only_security_group ID: $sec_group_id"
_info "Use these parameters for jenkins settings"
_info "================"


