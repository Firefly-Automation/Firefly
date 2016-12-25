#! /bin/bash

ask() {
    local prompt default REPLY
    while true; do
        if [ "${2:-}" = "Y" ]; then
            prompt="Y/n"
            default=Y
        elif [ "${2:-}" = "N" ]; then
            prompt="y/N"
            default=N
        else
            prompt="y/n"
            default=
        fi
        # Ask the question (not using "read -p" as it uses stderr not stdout)
        echo -n "$1 [$prompt] "
        # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
        read REPLY </dev/tty
        # Default?
        if [ -z "$REPLY" ]; then
            REPLY=$default
        fi
        # Check if the reply is valid
        case "$REPLY" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac
    done
}

if ask "Have you expanded the filesystem?"; then
	echo "Good"
else
	echo "Please expand the filesystem."
	echo "Please run 'sudo raspi-config' and select Expand Filesystem"
	exit
fi

if ask "Would you like to chnage the password for the default pi user?" Y; then
	passwd
else
	echo "It is recommended to chnage the defualt password if you have not already"
fi

if ask "Would you like to add the Firefly User." Y; then
	echo "Please fill out the following prompts to add the firefly user"
	sudo adduser firefly
	sudo adduser firefly sudo
fi

cd /opt
mkdir firefly_system
cd firefly_system

##################################
# INSTALL OPENZWAVE
##################################

echo "Installing Python OpenZWave... This might take some time.. Its a good time to go get a snack.. or Lunch.."

sudo apt-get install make build-esential libudev-dev build-essential python2.7-dev python-pip
wget https://github.com/OpenZWave/python-openzwave/raw/master/archives/python-openzwave-0.3.1.tgz
tar xvzf python-openzwave-0.3.1.tgz
cd python-openzwave-0.3.1
sudo make deps
make build
sudo make install

echo "Done installing Python OpenZWave!"

##################################
# INSTALL HA-BRIDGE
##################################

if ask "Do you want to install HA-Bridge for voice commands?" Y; then
	cd /opt/firefly_system
	sudo apt-get install openjdk-8-jre
	wget https://github.com/bwssytems/ha-bridge/releases/download/v3.5.1/ha-bridge-3.5.1.jar
fi

##################################
# INSTALL FIREFLY
##################################

echo "Installing Firefly Backend"

cd /opt/firefly_system
sudo apt-get install git mongodb
git clone https://github.com/zpriddy/Firefly.git



