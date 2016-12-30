#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root"
   exit 1
fi

FIREFLYROOT="/opt/firefly_system"

cd $FIREFLYROOT

if [ -e "$FIREFLYROOT/firefly.version" ]; then
    CURRENT_VERSION=line=$(head -1 $FIREFLYROOT)
else
    CURRENT_VERSION="a-0.0.1"
    echo "a-0.0.2" > firefly.version
fi

# Leaving this in for now, but when I can confirm that all configs are no longer stored here then I will remove it
cd $FIREFLYROOT
if [ ! -d "$FIREFLYROOT/.backup" ]; then
    mkdir .backup
fi
cp -r $FIREFLYROOT/Fiefly/Firefly/config $FIREFLYROOT/.backup
# End of TEMP

cd Firefly
git stash
git pull

cd $FIREFLYROOT

if [ "$CURRENT_VERSION" == "a-0.0.1" ]; then
    ##################################
    # COPY CONFIG FILES
    ##################################

    cd $FIREFLYROOT
    cp -r Firefly/setup_files/config .
    chown -R fiefly:firefly $FIREFLYROOT/config

    cp $FIREFLYROOT/Firefly/system_scripts/update_firefly.sh $FIREFLYROOT

    cp $FIREFLYROOT/.backup/devices.json $FIREFLYROOT/config/
    cp $FIREFLYROOT/.backup/location.json $FIREFLYROOT/config/
    cp $FIREFLYROOT/.backup/routine.json $FIREFLYROOT/config/

else
    cd $FIREFLYROOT
    cp Firefly/setup_files/config/*.sample.* $FIREFLYROOT/config
    chown -R fiefly:firefly $FIREFLYROOT/config
fi


cd $FIREFLYROOT/Serenity
git pull

if [ "$CURRENT_VERSION" == "a-0.0.1" ]; then
    ##################################
    # COPY CONFIG FILES
    ##################################

    cp $FIREFLYROOT/Serenity/serenity.config $FIREFLYROOT/config/

fi


# Leaving this in for now, but when I can confirm that all configs are no longer stored here then I will remove it
cp -r $FIREFLYROOT/.backup/config $FIREFLYROOT/FIrefly/Firefly/
# End of temp

sudo chown -R firefly:firefly /opt/firefly_system
