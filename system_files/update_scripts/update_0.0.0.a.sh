#!/usr/bin/env bash

FIREFLY_ROOT="/opt/firefly_system"
FIREFLY_META="/opt/firefly_system/.firefly"
FIREFLY_BACKUP="/opt/firefly_system/.firefly/backup"

if [ ! -f $FIREFLY_META/beacon_id ]; then
    BEACON_ID=$(cat /dev/urandom | tr -dc '0-9A-F' | fold -w 32 | head -n 1 | sed -e 's/\(..\)/\1 /g')
    echo "" >> $FIREFLY_ROOT/Firefly/dev_config/firefly.config
    echo beacon=$BEACON_ID >> $FIREFLY_ROOT/Firefly/dev_config/firefly.config
    echo $BEACON_ID > $FIREFLY_META/beacon_id
fi

cp $FIREFLY_ROOT/Firefly/system_files/ffbeacon.service /lib/systemd/system
chmod 644 /lib/systemd/system/ffbeacon.service
chmod +x $FIREFLY_ROOT/Firefly/system_files/firefly_beacon.sh
sudo systemctl daemon-reload
sudo systemctl enable ffbeacon.service

echo -e -n "/opt/firefly_system/logs/firefly_beacon.log {\n\tsize 100M\n\tcreate 766 root root\n\trotate 5\n}" >> /etc/logrotate.conf


echo "0.0.0.b" > $FIREFLY_META/current_version