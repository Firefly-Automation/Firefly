#!/usr/bin/env bash

cd /opt/firefly_system/Firefly
git pull

# This is a placeholder and in the future will do checks and stop/update/start firefly
bash /opt/firefly_system/Firefly/system_files/update_scripts/update_0-0-1.sh

exit 0