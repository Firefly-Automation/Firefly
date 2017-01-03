#! /bin/bash

FIREFLYROOT="/opt/firefly_system"
DOMAIN=$HOSTNAME

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

#################################
# ASK BASIC QUESTIONS
#################################

echo -e "\n\nThis is the Firefly install script. Please make sure that you have expanded your filesystem before running. It is recommended that you use a dynamic dns provider or have a domain setup for your home, Please see the readme for more info.\n\n"

if ask "Have you expanded the filesystem?"; then
	echo -e "Good"
else
	echo -e "Please expand the filesystem."
	echo -e "Please run 'sudo raspi-config' and select Expand Filesystem"
	exit
fi

if ask "Would you like to change the hostanme to Firefly" Y; then
  	DOMAIN="firefly"
  	sudo echo $DOMAIN > /etc/hostname
else
  	if ask "Would you like to set a custom hostname?" N; then
  	  	echo -e -c "What hostname would you like to use? "
  	  	read DOMAIN
  	  	sudo echo $DOMAIN > /etc/hostname
  	fi
fi


if ask "Would you like to change the password for the default pi user?" Y; then
	passwd
else
	echo -e "It is recommended to change the defualt password if you have not already"
fi

if ask "Would you like to add the Firefly User." Y; then
	echo -e "Please fill out the following prompts to add the firefly user"
	sudo adduser firefly
	sudo adduser firefly sudo
fi

#################################
# ASK FUTURE INSTALL QUESTIONS
#################################

ZWAVE_INSTALL=false
if ask "\n\nWould you like to install ZWave Support? This might take a while.. its a good time to get lunch.." Y; then
	ZWAVE_INSTALL=true
fi

HA_BRIDGE_INSTALL=false
if ask "\n\nDo you want to install HA-Bridge for voice commands?" Y; then
	HA_BRIDGE_INSTALL=true
fi

echo -e -n "\n\nPlease enter your email for git config (This does not require a github account ans is used only on this host.): "
read GIT_EMAIL

echo -e -n "Please enter your name for git config: "
read GIT_NAME


DYNAMIC_DOMAIN=false
LETS_ENCRYPT_INSTALL=false
SELF_SIGNED_CERT=false
EMAIL=""
echo -e "\n\nA dynamic dns domain will allow you to acccess your firefly system from anywhere. There are many options, the two I recommend are:"
echo -e "1) Google Domains (domains.google.com - \$12+/yr) - Google domains will allow you to choose any domain and set up a subdomain to access firefly, i.e. firefly.yourname.com"
echo -e "2) DuckDNS (duckdns.org - Free) - DuckDNS is a free  dynamic DNS provider and will allow you to have a domain like myName-firefly.duckdns.org to access your firefly system. However duckdns may be blocked by workplace firewalls."
if ask "Would you like to use a dynamic dns domain?"; then
	DYNAMIC_DOMAIN=true
	echo -e -n "\n\nPlease enter the external domain for Firefly. [ENTER]: "
	read DOMAIN
	echo $DOMAIN > /etc/hostname

	if ask "\n\nWould you like to install and setup LetsEncrypt? This requires a dynamic dns domain to have been setup and port 443 to be forwarded to the pi."; then
		LETS_ENCRYPT_INSTALL=true
		echo -e -n "\n\Please enter you email. [ENTER]: "
		read EMAIL
	fi
fi




COUNTRY=""
STATE=""
LOCALITY=""

if ! $LETS_ENCRYPT_INSTALL ; then
  	echo -e "\n\nWe will then generate a self signed ssl cert for your system. The next few questions are for that."
  	SELF_SIGNED_CERT=true
  	echo -e -n "Please enter your country: "
  	read COUNTRY

  	echo -e -n "Please enter your state: "
  	read STATE

  	echo -e -n "Please enter your locality: "
  	read LOCALITY

  	echo -e -n "\n\Please enter you email: "
    read EMAIL
fi

#################################
# DONE ASKING QUESTIONS
#################################


#################################
# UPDATE PI
#################################

echo -e "\n\nUpdating RaspberryPi...\n\n"
sudo apt-get update
sudo apt-get dist-upgrade -y

#################################
# MAKE OPT/FIREFLY_SYSTEM
#################################

cd /opt
mkdir firefly_system
cd firefly_system

##################################
# INSTALL OPENZWAVE
##################################
if $ZWAVE_INSTALL; then
	echo -e "\n\nInstalling Python OpenZWave... This might take some time.. Its a good time to go get a snack.. or Lunch..\n\n"

	cd $FIREFLYROOT
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
	cd $FIREFLYROOT
	rm python-openzwave-0.3.1.tgz

	python -c "import openzwave"
	if [ $? == 1 ]; then
		cd $FIREFLYROOT/python-openzwave-0.3.1/openzwave/
		sudo make clean
		sudo make build
		sudo make install
	fi
	echo -e "\n\nDone installing Python OpenZWave!\n\n"
fi

##################################
# INSTALL HA-BRIDGE
##################################

if $HA_BRIDGE_INSTALL; then
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

MONGO_VERSION="$(mongo --version)"
if [[ $MONGO_VERSION =~ "3.0.9" ]]; then
	echo -e "Mongo already installed!"
else
	if [ !$MONGOUSER ]; then
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
		sudo chmod +x /lib/systemd/system/mongodb.service

		sudo mkdir /data
		sudo chown -R mongodb:root /data

		sudo mkdir /data/db
		sudo chown -R mongodb:root /data/db

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

if $DYNAMIC_DOMAIN; then

	echo -e "\n\nTBD - Add chron job for updating dynamic dns doamin."


	##################################
	# INSTALL LETS ENCRYPT
	##################################

	if $LETS_ENCRYPT_INSTALL; then
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

		cd $FIREFLYROOT
		sudo ./certbot-auto certonly --standalone --standalone-supported-challenges tls-sni-01 --agree-tos --email $EMAIL -d $DOMAIN

		echo -e "\n\nFinished installing first cert\n\n"
	fi
fi

##################################
# INSTALL SELF SIGNED CERT
##################################
if $SELF_SIGNED_CERT ; then
	sudo apt-get install -y openssl

	cd $FIREFLYROOT
	mkdir .ssl
	cd .ssl
	password=dummypassword
	echo "Generating key request for $DOMAIN"
	openssl genrsa -des3 -passout pass:$password -out $DOMAIN.key 2048 -noout
	openssl rsa -in $DOMAIN.key -passin pass:$password -out $DOMAIN.key
	openssl req -new -key $DOMAIN.key -out $DOMAIN.csr -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=FIREFLY/OU=AUTOMATION/CN=$DOMAIN/emailAddress=$EMAIL"
	openssl x509 -req -days 3650 -in $DOMAIN.csr -signkey $DOMAIN.key -out $DOMAIN.crt

	mkdir /etc/letsencrypt/
	mkdir /etc/letsencrypt/live
	mkdir /etc/letsencrypt/live/$DOMAIN
	cp $DOMAIN.key /etc/letsencrypt/live/$DOMAIN/privkey.pem
	cp $DOMAIN.crt /etc/letsencrypt/live/$DOMAIN/fullchain.pem

fi


##################################
# INSTALL SERENITY [TODO]
##################################

echo -e "\n\nInstalling Serenity WEB UI\n\n"

sudo apt-get install -y nginx libffi-dev python-bcrypt
sudo chown -R www-data:www-data /var/www/firefly_www

cd $FIREFLYROOT

if [ -d "$FIREFLYROOT/Serenity" ]; then
	cd $FIREFLYROOT/Serenity
	git pull
else
	git clone https://github.com/zpriddy/Serenity.git
fi

cd $FIREFLYROOT/Serenity
cp serenity.config $FIREFLYROOT/config/
sudo pip install -r requirements.txt

sed "s/<<DOMAIN>>/$DOMAIN/" nginx.confg > /etc/nginx/sites-enabled/default

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

# TODO (Replace the startup script with a nice service like script)
cd $FIREFLYROOT/Firefly/system_scripts
cp firefly_initd.sh /etc/init.d/firefly
chmod +x /etc/init.d/firefly
chmod 755 /etc/init.d/firefly
sudo update-rc.d firefly defaults

# OPTIONAL: Start web browser to UI in fullscreen

# Copy update script
cp FIREFLYROOT/Firefly/system_scripts/update_firefly.sh $FIREFLYROOT

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
# COPY CONFIG FILES
# on updates it will only copy *.sample.*
##################################

git config --global user.email $GIT_EMAIL
git config --global user.name $GIT_NAME

cd $FIREFLYROOT
cp -r Firefly/setup_files/config .

# copy the update script for easy updates
cp $FIREFLYROOT/Firefly/system_scripts/update_firefly.sh $FIREFLYROOT


##################################
# CLEANUP
##################################

echo $DOMAIN > $FIREFLYROOT/config/.domain
echo "a-0.0.2" > $FIREFLYROOT/.firefly.version

sudo chown -R firefly:firefly /opt/firefly_system

# reboot to finish setup
if ask "Would you like to reboot now?" Y; then
	sudo reboot
fi