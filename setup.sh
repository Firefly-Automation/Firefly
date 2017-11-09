#!/usr/bin/env bash

FIREFLY_ROOT="/opt/firefly_system"
FIREFLY_META="/opt/firefly_system/.firefly"
FIREFLY_BACKUP="/opt/firefly_system/.firefly/backup"

if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root"
   exit 1
fi

apt-get dist-upgrade -y

echo ""
echo "******************************************************"
echo " INSTALLING PYTHON 3.6 VIA BERRYCONDA"
echo "******************************************************"
echo ""

mkdir $FIREFLY_ROOT
cd $FIREFLY_ROOT
wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
sudo bash Berryconda3-2.0.0-Linux-armv7l.sh -b -p $FIREFLY_ROOT/berryconda

# System Links to python binaries
sudo ln -s $FIREFLY_ROOT/berryconda/bin/pip /usr/bin/pip3.6
sudo ln -s $FIREFLY_ROOT/berryconda/bin/pydoc3.6 /usr/bin/pydoc3.6
sudo ln -s $FIREFLY_ROOT/berryconda/bin/python3.6-config /usr/bin/python3.6-config
sudo ln -s $FIREFLY_ROOT/berryconda/bin/python3.6 /usr/bin/python3.6


echo ""
echo "******************************************************"
echo " INSTALLING PYTHON OPEN ZWAVE"
echo "******************************************************"
echo ""

sudo apt-get install --force-yes -y make libudev-dev g++ libyaml-dev
sudo pip3.6 install python_openzwave

echo ""
echo "******************************************************"
echo " INSTALLING FIREFLY"
echo "******************************************************"
echo ""

cd $FIREFLY_ROOT
git clone https://github.com/zpriddy/forecastiopy.git
cd forecastiopy/
python3.6 setup.py install

pip3.6 install pytz
cd $FIREFLY_ROOT
git clone https://github.com/zpriddy/astral.git
cd astral/
python3.6 setup.py install

cd $FIREFLY_ROOT
git clone https://github.com/zpriddy/Pyrebase.git
cd Pyrebase
pip3.6 install -r requirements.txt
python3.6 setup.py install

cd $FIREFLY_ROOT
git clone https://github.com/Firefly-Automation/Firefly.git
# TODO: Leave this as master
git checkout beta
cd Firefly
pip3.6 install -r requirements.txt
# TODO: Make this just config in the future
mkdir dev_config
cd dev_config
mkdir services
cd ..
cp sample_config/firefly.config dev_config/
cp sample_config/device_alias.json dev_config/
echo [] > dev_config/automation.jsonecho [] > dev_config/automation.json

#####################################
# SETUP BEACON
#####################################
mkdir $FIREFLY_META
BEACON_ID=$(cat /dev/urandom | tr -dc '0-9A-F' | fold -w 32 | head -n 1 | sed -e 's/\(..\)/\1 /g')
echo \beacon=$BEACON_ID >> $FIREFLY_ROOT/Firefly/dev_config/firefly.config
echo $BEACON_ID > $FIREFLY_META/beacon_id

#####################################
# RECORD UPDATE VERSION
#####################################
echo "b.0.0.1" > $FIREFLY_META/current_version

#####################################
# SETUP AUTO-START
#####################################
cd $FIREFLY_ROOT/Firefly/system_files
bash setup_autostart.sh
