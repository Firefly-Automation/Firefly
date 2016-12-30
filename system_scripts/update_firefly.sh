#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root"
   exit 1
fi

FIREFLYROOT="/opt/firefly_system"

cd $FIREFLYROOT
if [ -d $FIREFLYROOT/.update ]; then
    cd .update
    rm update_firefly.sh
else
    mkdir .update
    cd .update
fi

wget https://raw.githubusercontent.com/zpriddy/Firefly/master/update_firefly.sh

sudo bash update_firefly.sh