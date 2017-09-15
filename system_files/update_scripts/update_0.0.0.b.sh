#!/usr/bin/env bash

FIREFLY_ROOT="/opt/firefly_system"
FIREFLY_META="/opt/firefly_system/.firefly"
FIREFLY_BACKUP="/opt/firefly_system/.firefly/backup"

cd $FIREFLY_ROOT/Firefly
sudo pip3.6 install -r requirements.txt

echo "" >> $FIREFLY_ROOT/Firefly/dev_config/services.config
echo "[NEST]" >> $FIREFLY_ROOT/Firefly/dev_config/services.config
echo "enable = true" >> $FIREFLY_ROOT/Firefly/dev_config/services.config
echo "package = Firefly.services.nest" >> $FIREFLY_ROOT/Firefly/dev_config/services.config
echo "" >> $FIREFLY_ROOT/Firefly/dev_config/services.config

sudo service firefly restart

echo "0.0.0.c" > $FIREFLY_META/current_version