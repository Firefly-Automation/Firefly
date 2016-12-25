#! /bin/bash

FIREFLYROOT="/opt/firefly_system"
DOMAIN=""

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

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
if ask "\n\nWould you like to install ZWave Support? This might take a while.. its a good time to get lunch.." Y; then
	echo "\n\nInstalling Python OpenZWave... This might take some time.. Its a good time to go get a snack.. or Lunch..\n\n"

	cd /opt/firefly_system
	sudo apt-get install -y make build-esential libudev-dev build-essential python2.7-dev python-pip libu
	wget https://github.com/OpenZWave/python-openzwave/raw/master/archives/python-openzwave-0.3.1.tgz
	tar xvzf python-openzwave-0.3.1.tgz
	cd python-openzwave-0.3.1
	sudo make clean
	sudo make deps
	sudo make build
	sudo make install
	cd /opt/firefly_system
	rm python-openzwave-0.3.1.tgz

	echo "\n\nDone installing Python OpenZWave!\n\n"
fi

##################################
# INSTALL HA-BRIDGE
##################################

if ask "\n\nDo you want to install HA-Bridge for voice commands?" Y; then
	cd /opt/firefly_system
	mkdir ha_bridge
	cd ha_bridge
	rm ha-bridge-*.jar
	sudo apt-get install -y openjdk-8-jre
	wget https://github.com/bwssytems/ha-bridge/releases/download/v3.5.1/ha-bridge-3.5.1.jar
fi

##################################
# INSTALL FIREFLY
##################################

echo "\n\nInstalling Firefly Backend\n\n"

cd /opt/firefly_system
sudo apt-get install -y git mongodb
if [ -d "$FIREFLYROOT/Firefly" ]; then
	cd $FIREFLYROOT/Firefly
	git pull
else
	git clone https://github.com/zpriddy/Firefly.git
fi
cd $FIREFLYROOT/Firefly/Firefly
sudo pip install -r requirements.txt

echo "\n\nDone Installing Firefly Backend\n\n"

##################################
# INSTALL ASK FOR DYNAMIC DNS
##################################

echo "\n\nA dynamic dns domain will allow you to acccess your firefly system from anywhere. There are many options, the two I recommend are:"
echo "1) Google Domains (domains.google.com - \$12+/yr) - Google domains will allow you to choose any domain and set up a subdomain to access firefly, i.e. firefly.yourname.com"
echo "2) DuckDNS (duckdns.org - Free) - DuckDNS is a free  dynamic DNS provider and will allow you to have a domain like myName-firefly.duckdns.org to access your firefly system. However duckdns may be blocked by workplace firewalls."
if ask "Would you like to use a dynamic dns domain?"; then

	echo -n "\n\nPlease enter the external domain for Firefly. [ENTER]:"
	read DOMAIN

	echo "\n\nTBD - Add chron job for updating dynamic dns doamin."


	##################################
	# INSTALL LETS ENCRYPT
	##################################

	if ask "\n\nWould you like to install and setup LetsEncrypt? This requires a dynamic dns domain to have been setup."; then
		echo "\n\nInstalling LetsEncrypt and getting first certificate.\n\n"

		sudo apt-get -y install certbot
		cd /var/www
		sudo mkdir firefly_www
		cd firefly_www
		sudo mkdir .well-known
		cd .well-known
		sudo mkdir acme-challenge
		cd /var/www
		sudo chown -R www-data:www-data firefly_www

		echo -n "\n\nPlsease enter you email. [ENTER]:"
		read EMAIL
		certbot certonly --standalone --standalone-supported-challenges tls-sni-01 --agree-tos --email $EMAIL -d $DOMAIN

		echo "\n\nFinished installing first cert\n\n"
	fi 
fi



##################################
# INSTALL SERENITY
##################################

echo "\n\nInstalling Serenity WEB UI\n\n"

sudo apt-get install -y nginx

if [ -d "$FIREFLYROOT/Serenity" ]; then
	cd $FIREFLYROOT/Serenity
	git pull
else
	git clone https://github.com/zpriddy/Serenity.git
fi

cd $FIREFLYROOT/Serenity
sudo pip install -r requirements.txt

# Need to update and copy the nginx config - if not dynamic DNS then need to chnage to port 80 instead.
# Need to then restart nginx

echo "\n\nThe nginx config has not been automated out yet. Please copy the nginx config from: /opt/firefly_system/Serenity/nginx.confg to /etx/nginx/sites-enabled/default"
echo "After copying this file please edit it do that the domains are correct."

##################################
# INSTALL AUTO-START SCRIPTS
##################################

# Need to verify permissions of serial port
# Need to start Firefly on boot
# Need to start Serenity on boot
# Need to start ha-bridge on boot
echo "\n\nSetting Firefly to start on boot.\n\n"
cd $FIREFLYROOT/Firefly
cp firefly_startup.sh $FIREFLYROOT
cd $FIREFLYROOT
chmod +x firefly_startup.sh
(sudo crontab -l; echo "@reboot /opt/firefly_system/firefly_startup.sh &") | crontab -

# OPTIONAL: Start web browser to UI in fullscreen

##################################
# INSTALL LETS ENCRYPT RENEWAL
##################################

#certbot renew --pre-hook "service nginx stop" --post-hook "service nginx start" --standalone --standalone-supported-challenges tls-sni-01 --agree-tos --email $EMAIL -d $DOMAIN

##################################
# SET PASSWORD ETC
##################################

# ask for Admin password
# Set password in config file for serenity
# On reboot it should then apply the new admin password

echo "\n\nThe default username is admin and the password is FireflyPassword1234. PLEASE CHANGE THIS PASSWORD WHEN YOU LOG IN!!\n\n"

##################################
# CLEANUP
##################################

cd /opt/firefly_system
sudo chown -R firefly:firefly * 

# reboot to finish setup
if ask "Would you like to reboot now?" Y; then
	sudo reboot
fi