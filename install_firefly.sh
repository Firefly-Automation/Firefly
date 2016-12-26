#! /bin/bash

FIREFLYROOT="/opt/firefly_system"
DOMAIN=""

if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root" 
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
        echo -e -n "$1 [$prompt] "
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

echo -e "\n\nThis is the Firefly install script. Please make sure that you have expanded your filesystem before running. It is recommended that you use a dynamic dns provider or have a domain setup for you home, Please see the readme for more info.\n\n"

if ask "Have you expanded the filesystem?"; then
	echo -e "Good"
else
	echo -e "Please expand the filesystem."
	echo -e "Please run 'sudo raspi-config' and select Expand Filesystem"
	exit
fi

if ask "Would you like to chnage the password for the default pi user?" Y; then
	passwd
else
	echo -e "It is recommended to chnage the defualt password if you have not already"
fi

if ask "Would you like to add the Firefly User." Y; then
	echo -e "Please fill out the following prompts to add the firefly user"
	sudo adduser firefly
	sudo adduser firefly sudo
fi

echo -e "\n\nUpdating RaspberryPi...\n\n"
sudo apt-get update
sudo apt-get dist-upgrade

cd /opt
mkdir firefly_system
cd firefly_system

##################################
# INSTALL OPENZWAVE
##################################
if ask "\n\nWould you like to install ZWave Support? This might take a while.. its a good time to get lunch.." Y; then
	echo -e "\n\nInstalling Python OpenZWave... This might take some time.. Its a good time to go get a snack.. or Lunch..\n\n"

	cd /opt/firefly_system
	sudo apt-get install -y make build-esential libudev-dev build-essential python2.7-dev python-pip libu
	# Not sure why libudev-dev game me an error.. But trying this fix..
	sudo apt-get install -y libudev-dev 
	wget https://github.com/OpenZWave/python-openzwave/raw/master/archives/python-openzwave-0.3.1.tgz
	tar xvzf python-openzwave-0.3.1.tgz
	cd python-openzwave-0.3.1
	sudo make clean
	sudo make deps
	sudo make build
	sudo make install
	cd /opt/firefly_system
	rm python-openzwave-0.3.1.tgz

	echo -e "\n\nDone installing Python OpenZWave!\n\n"
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
# INSTALL MONGO
##################################
echo -e "\n\nInstalling MongoDB\n\n"

MONGOUSER=false
mongodb passwd $1 >/dev/null 2>&1 && MONGOUSER=true
if [ ! $MONGOUSER ]; then
	sudo adduser --ingroup nogroup --shell /etc/false --disabled-password --gecos "" --no-create-home mongodb
fi
if [ ! -d "$FIREFLYROOT/mongodb" ]; then 
	cd $FIREFLYROOT
	mkdir mongodb
	cd mongodb
	wget https://github.com/zpriddy/Firefly/releases/download/0.0.1-alpha/core_mongodb.tar.gz
	wget https://github.com/zpriddy/Firefly/releases/download/0.0.1-alpha/tools_mongodb.tar.gz

	tar xvzf core_mongodb.tar.gz
	cd core_mongodb

	sudo chown root:root mongo*
	sudo chmod 755 mongo*
	sudo strip mongo*
	sudo cp -p mongo* /usr/bin

	sudo mkdir /var/log/mongodb
	sudo chown mongodb:nogroup /var/log/mongodb

	sudo mkdir /var/lib/mongodb
	sudo chown mongodb:root /var/lib/mongodb
	sudo chmod 775 /var/lib/mongodb
	
	echo -e "# /etc/mongodb.conf\n# minimal config file (old style)\n# Run mongod --help to see a list of options\n\nbind_ip = 127.0.0.1\nquiet = true\ndbpath = /var/lib/mongodb\nlogpath = /var/log/mongodb/mongod.log\nlogappend = true\nstorageEngine = mmapv1" > /etc/mongodb.conf

	echo -e "[Unit]\nDescription=High-performance, schema-free document-oriented database\nAfter=network.target\n\n[Service]\nUser=mongodb\nExecStart=/usr/bin/mongod --quiet --config /etc/mongodb.conf\n\n[Install]\nWantedBy=multi-user.target" > /lib/systemd/system/mongodb.service

	sudo service mongodb start

	cd $FIREFLYROOT/mongodb
	tar zxvf tools_mongodb.tar.gz
	sudo strip mongo*
	sudo chown root:root mongo*
	sudo chmod 755 mongo*
	sudo mv mongo* /usr/bin

	echo -e "\n\nFinished installing Mongo\n\n"
else
	echo -e "\n\n!!!!!!! ERROR INSTALLING MONGO !!!!!!!\n\n"
fi


##################################
# INSTALL FIREFLY
##################################

echo -e "\n\nInstalling Firefly Backend\n\n"

cd /opt/firefly_system
if [ -d "$FIREFLYROOT/Firefly" ]; then
	cd $FIREFLYROOT/Firefly
	git pull
else
	git clone https://github.com/zpriddy/Firefly.git
fi
cd $FIREFLYROOT/Firefly/Firefly
sudo pip install -r requirements.txt

echo -e "\n\nDone Installing Firefly Backend\n\n"

##################################
# INSTALL ASK FOR DYNAMIC DNS
##################################

echo -e "\n\nA dynamic dns domain will allow you to acccess your firefly system from anywhere. There are many options, the two I recommend are:"
echo -e "1) Google Domains (domains.google.com - \$12+/yr) - Google domains will allow you to choose any domain and set up a subdomain to access firefly, i.e. firefly.yourname.com"
echo -e "2) DuckDNS (duckdns.org - Free) - DuckDNS is a free  dynamic DNS provider and will allow you to have a domain like myName-firefly.duckdns.org to access your firefly system. However duckdns may be blocked by workplace firewalls."
if ask "Would you like to use a dynamic dns domain?"; then

	echo -e -n "\n\nPlease enter the external domain for Firefly. [ENTER]:"
	read DOMAIN

	echo -e "\n\nTBD - Add chron job for updating dynamic dns doamin."


	##################################
	# INSTALL LETS ENCRYPT
	##################################

	if ask "\n\nWould you like to install and setup LetsEncrypt? This requires a dynamic dns domain to have been setup."; then
		echo -e "\n\nInstalling LetsEncrypt and getting first certificate.\n\n"

		#sudo apt-get -y install certbot
		cd $FIREFLYROOT
		wget https://dl.eff.org/certbot-auto
		chmod a+x certbot-auto
		if [ ! -d "/var/www" ]; then
			sudo mkdir /var/www
		fi
		if [ ! -d "/var/www/firefly_www" ]; then
			sudo mkdir /var/www/firefly_www
		fi
		if [ ! -d "/var/www/firefly_www.well-known" ]; then
			sudo mkdir /var/www/firefly_www/.well-known
		fi
		if [ ! -d "var/www/firefly_www/.well-known/acme-challenge" ]; then
			sudo mkdir /var/www/firefly_www/.well-known/acme-challenge
		fi

		echo -e -n "\n\nPlsease enter you email. [ENTER]:"
		read EMAIL
		cd $FIREFLYROOT
		sudo ./certbot-auto certonly --standalone --standalone-supported-challenges tls-sni-01 --agree-tos --email $EMAIL -d $DOMAIN

		echo -e "\n\nFinished installing first cert\n\n"
	fi 
fi



##################################
# INSTALL SERENITY [TODO]
##################################

echo -e "\n\nInstalling Serenity WEB UI\n\n"

sudo apt-get install -y nginx
sudo chown -R www-data:www-data /var/www/firefly_www

cd $FIREFLYROOT

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

#echo -e "\n\nThe nginx config has not been automated out yet. Please copy the nginx config from: /opt/firefly_system/Serenity/nginx.confg to /etx/nginx/sites-enabled/default"
#echo -e "After copying this file please edit it do that the domains are correct."

sed "s/<<DOMAIN>>/$DOMAIN/" nginx.confg > /etx/nginx/sites-enabled/default

##################################
# INSTALL AUTO-START SCRIPTS [TODO]
##################################

# Need to verify permissions of serial port
# Need to start Firefly on boot
# Need to start Serenity on boot
# Need to start ha-bridge on boot
echo -e "\n\nSetting Firefly to start on boot.\n\n"
cd $FIREFLYROOT/Firefly
cp firefly_startup.sh $FIREFLYROOT
cd $FIREFLYROOT
chmod +x firefly_startup.sh
(sudo crontab -l; echo -e "@reboot /opt/firefly_system/firefly_startup.sh &") | crontab -

cd $FIREFLYROOT/Firefly/sysetm_scripts
cp firefly_initd.sh /etc/init.d/firefly
chmod +x /etc/init.d/firefly
chmod 755 /etc/init.d/firefly
update-rc.d firefly defaults

# OPTIONAL: Start web browser to UI in fullscreen

##################################
# INSTALL LETS ENCRYPT RENEWAL [TODO]
##################################

#certbot renew --pre-hook "service nginx stop" --post-hook "service nginx start" --standalone --standalone-supported-challenges tls-sni-01 --agree-tos --email $EMAIL -d $DOMAIN

##################################
# SET PASSWORD ETC [TODO]
##################################

# ask for Admin password
# Set password in config file for serenity
# On reboot it should then apply the new admin password

echo -e "\n\nThe default username is admin and the password is FireflyPassword1234. PLEASE CHANGE THIS PASSWORD WHEN YOU LOG IN!!\n\n"

##################################
# CLEANUP
##################################

cd /opt
sudo chown -R firefly:firefly firefly_system 

# reboot to finish setup
if ask "Would you like to reboot now?" Y; then
	sudo reboot
fi