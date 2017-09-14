#!/usr/bin/env bash

FIREFLY_ROOT="/opt/firefly_system"
FIREFLY_META="/opt/firefly_system/.firefly"
FIREFLY_BACKUP="/opt/firefly_system/.firefly/backup"

if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root"
   exit 1
fi

sudo apt-get dist-upgrade -y

mkdir $FIREFLY_ROOT
mkdir $FIREFLY_ROOT/python3.6
cd $FIREFLY_ROOT/python3.6
sudo apt-get install -y build-essential checkinstall
sudo apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar xzvf Python-3.6.1.tgz
cd Python-3.6.1/
./configure
sudo make install

sudo rm /usr/bin/pip3
sudo rm /usr/bin/python3-config
sudo rm /usr/bin/python3

sudo pip3 install docutils pygments roman
cd $FIREFLY_ROOT
git clone https://github.com/OpenZWave/python-openzwave.git
cd python-openzwave/
sudo make common-deps PYTHON_EXEC=python3
make build PYTHON_EXEC=python3
sudo pip3 install cython
sudo make install PYTHON_EXEC=python3


cd $FIREFLY_ROOT
git clone https://github.com/zpriddy/forecastiopy.git
cd forecastiopy/
sudo python3 setup.py install

sudo pip3 install pytz
cd $FIREFLY_ROOT
git clone https://github.com/zpriddy/astral.git
cd astral/
sudo python3 setup.py install

cd $FIREFLY_ROOT
git clone https://github.com/zpriddy/Pyrebase.git
cd Pyrebase
sudo pip3 install -r requirements.txt
sudo python3 setup.py install

cd $FIREFLY_ROOT
git clone https://github.com/Firefly-Automation/Firefly.git
cd Firefly
sudo pip3 install -r requirements.txt
cp -r sample_config dev_config
echo [] > dev_config/automation.json

#####################################
# SETUP BEACON
#####################################
BEACON_ID=$(cat /dev/urandom | tr -dc '0-9A-F' | fold -w 32 | head -n 1 | sed -e 's/\(..\)/\1 /g')
echo \beacon=$BEACON_ID >> $FIREFLY_ROOT/Firefly/dev_config/firefly.config
echo $BEACON_ID > $FIREFLY_META/beacon_id

#####################################
# RECORD UPDATE VERSION
#####################################
echo "0.0.0.b" > $FIREFLY_META/current_version

#####################################
# SETUP AUTO-START
#####################################
cd $FIREFLY_ROOT/Firefly/system_files
sudo bash setup_autostart.sh