#!/usr/bin/env bash

FIREFLYROOT="/opt/firefly_system"

if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root"
   exit 1
fi

DATE=$(date --iso-8601)
mkdir -p $FIREFLYROOT/.backup
tar cvzf $FIREFLYROOT/.backup/firefly-backup-$DATE.tar.gz $FIREFLYROOT/config

cd $FIREFLYROOT/Firefly
git stash
git pull

cd $FIREFLYROOT/Serenity
git stash
git pull

cd $FIREFLYROOT/Firefly/setup_files/
find  config/ -name '*.sample.*' -exec cp -pvr --parents '{}' $FIREFLYROOT ';'

systemctl restart firefly.service
systemctl restart serenity.service

chown -R firefly:firefly $FIREFLYROOT
