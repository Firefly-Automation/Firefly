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
echo " INSTALLING PYTHON 3.6"
echo "******************************************************"
echo ""

mkdir $FIREFLY_ROOT
mkdir $FIREFLY_ROOT/python3.6
cd $FIREFLY_ROOT/python3.6
apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-devibc6-dev
wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz
tar xzvf Python-3.6.2.tgz
cd Python-3.6.2/
./configure
make -j 4
sudo make altinstall


echo ""
echo "******************************************************"
echo " INSTALLING PYTHON OPEN ZWAVE"
echo "******************************************************"
echo ""

pip3.6 install docutils pygments roman
cd $FIREFLY_ROOT
git clone https://github.com/OpenZWave/python-openzwave.git
cd python-openzwave/
make common-deps PYTHON_EXEC=python3
make build PYTHON_EXEC=python3
pip3.6 install cython
make install PYTHON_EXEC=python3

echo ""
echo "******************************************************"
echo " INSTALLING PFIREFLY"
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
cd Firefly
pip3.6 install -r requirements.txt
cp -r sample_config dev_config
echo [] > dev_config/automation.json

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
echo "0.0.0.b" > $FIREFLY_META/current_version

#####################################
# SETUP AUTO-START
#####################################
cd $FIREFLY_ROOT/Firefly/system_files
bash setup_autostart.sh