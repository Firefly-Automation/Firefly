#!/usr/bin/env bash
FIREFLY_META="/opt/firefly_system/.firefly"

BLUETOOTH_DEVICE=hci0
UUID=$(cat $FIREFLY_META/beacon_id)
MAJOR="00 01"
MINOR="00 01"
POWER="c5"

sudo hciconfig $BLUETOOTH_DEVICE up
sudo hciconfig $BLUETOOTH_DEVICE noleadv
sudo hciconfig $BLUETOOTH_DEVICE leadv 0
sudo hcitool -i hci0 cmd 0x08 0x0008 1e 02 01 1a 1a ff 4c 00 02 15 $UUID $MAJOR $MINOR $POWER 00