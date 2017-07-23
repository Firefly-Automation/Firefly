#!/usr/bin/env bash

FIREFLY_ROOT="/opt/firefly_system"
FIREFLY_META="/opt/firefly_system/.firefly"
FIREFLY_BACKUP="/opt/firefly_system/.firefly/backup"
FIREFLY_CONFIG="/opt/firefly_system/Firefly/dev_config"
FIREFLY_UPDATE_PATH="/opt/firefly_system/Firefly/system_files/update_scripts"

if [ ! -d "$FIREFLY_META" ]; then
    mkdir $FIREFLY_META
fi
if [ ! -d "$FIREFLY_BACKUP" ]; then
    mkdir $FIREFLY_BACKUP
fi

cd $FIREFLY_BACKUP
if [ $(ls -1 | grep ^backup | wc -l) -eq 5 ]; then
    rm -rf backup_5
fi
if [ $(ls -1 | grep ^backup | wc -l) -ge 4 ]; then
    mv backup_4 backup_5
fi
if [ $(ls -1 | grep ^backup | wc -l) -ge 3 ]; then
    mv backup_3 backup_4
fi
if [ $(ls -1 | grep ^backup | wc -l) -ge 2 ]; then
    mv backup_2 backup_3
fi
if [ $(ls -1 | grep ^backup | wc -l) -ge 1 ]; then
    mv backup_1 backup_2
fi
cp -r $FIREFLY_CONFIG backup_1
cd backup_1
touch ".$(date +%F_%R)"
cd $FIREFLY_BACKUP


cd /opt/firefly_system/Firefly
git pull

if [ ! -f $FIREFLY_META/current_version ]; then
    # This is a placeholder and in the future will do checks and stop/update/start firefly
    bash /opt/firefly_system/Firefly/system_files/update_scripts/update_0.0.0.a.sh
fi

UPDATE_SCRIPT="update_from$(cat $FIREFLY_META/current_version).sh"
if [ -f $FIREFLY_UPDATE_PATH/$UPDATE_SCRIPT ]; then
    bash $FIREFLY_UPDATE_PATH/$UPDATE_SCRIPT
fi

exit 0