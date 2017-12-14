#!/bin/bash
#
# Simple script that updates the IP address to proxy pass
#
# Arguments:
# - $1: IPv4 address to change
#

# From http://www.linuxjournal.com/content/validating-ip-address-bash-script
function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

if [ -z $1 ]; then
    echo "Usage: change_proxy.sh (ip)"
    exit 1
fi

if ! valid_ip $1; then
    echo "Invalid IPv4 address"
    exit 1
fi

echo "proxy_pass http://$1;" | sudo tee /etc/nginx/proxy_pass/root_pass.conf
sudo nginx -s reload
