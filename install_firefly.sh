#! /bin/bash

FIREFLY_ROOT="/opt/firefly_system"
FIREFLY_CONFIG="/opt/firefly/config"
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
# MAKE OPT/FIREFLY_SYSTEM
#################################

mkdir -p $FIREFLY_ROOT
mkdir -p $FIREFLY_ROOT/config


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
  	echo $DOMAIN > /etc/hostname
else
  	if ask "Would you like to set a custom hostname?" N; then
  	  	echo -e -c "What hostname would you like to use? "
  	  	read DOMAIN
  	  	echo $DOMAIN > /etc/hostname
  	fi
fi


if ask "Would you like to change the password for the default pi user?" Y; then
	passwd
else
	echo -e "It is recommended to change the defualt password if you have not already"
fi


echo -e "We are now adding a default Firefly user.\n Please fill out the following prompts to add the firefly user\n\m"
adduser firefly
adduser firefly sudo


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


if [ ! -f ~/.gitconfig ]; then
    echo -e -n "\n\nPlease enter your email for git config (This does not require a github account ans is used only on this host.): "
    read GIT_EMAIL

    echo -e -n "Please enter your name for git config: "
    read GIT_NAME

    # Copy this git config to the other users too.
    cp ~/.gitconfig /home/pi
    chown pi /home/pi/.gitconfig
    cp ~/.gitconfig /home/firefly
    chown pi /home/firefly/.gitconfig
fi



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
	echo $DOMAIN > $FIREFLY_CONFIG/.domain

	if ask "\n\nWould you like to install and setup LetsEncrypt? This requires a dynamic dns domain to have been setup and port 443 to be forwarded to the pi."; then
		LETS_ENCRYPT_INSTALL=true
		echo -e -n "\n\nPlease enter you email. [ENTER]: "
		read EMAIL
		echo $EMAIL > $FIREFLY_CONFIG/.letsencrypt_email
	fi
else
    echo "FALSE" > $FIREFLY_CONFIG/.domain
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

echo -e "\n\nAbout to update the raspberryPi. There may be some required interactions during this process. Please check every once in a while. If there is a screen of text telling you about a change you should be able to press q to continue.\n\n"
read -n 1 -s -p "Press any key to continue"
apt-get update
apt-get dist-upgrade -y


##################################
# INSTALL OPENZWAVE
##################################
if $ZWAVE_INSTALL; then
	echo -e "\n\nInstalling Python OpenZWave... This might take some time.. Its a good time to go get a snack.. or Lunch..\n\n"

	cd $FIREFLY_ROOT
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
	cd $FIREFLY_ROOT
	rm python-openzwave-0.3.1.tgz

	python -c "import openzwave"
	if [ $? == 1 ]; then
		cd $FIREFLY_ROOT/python-openzwave-0.3.1/openzwave/
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
	if [ ! -d "$FIREFLY_ROOT/mongodb" ]; then
		cd $FIREFLY_ROOT
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

		cd $FIREFLY_ROOT/mongodb
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
if [ -d "$FIREFLY_ROOT/Firefly" ]; then
	cd $FIREFLY_ROOT/Firefly
	git pull
else
	git clone https://github.com/zpriddy/Firefly.git
fi
cd $FIREFLY_ROOT/Firefly/Firefly
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
		cd $FIREFLY_ROOT
		wget https://dl.eff.org/certbot-auto
		chmod a+x certbot-auto

		mkdir -p /var/www/firefly_www/.well-known/acme-challenge

		cd $FIREFLY_ROOT
		./certbot-auto certonly --standalone --standalone-supported-challenges tls-sni-01 --agree-tos --email $EMAIL -d $DOMAIN --noninteractive

		echo -e "\n\nFinished installing first cert\n\n"
	fi
fi

##################################
# INSTALL SELF SIGNED CERT
##################################
if $SELF_SIGNED_CERT ; then
	sudo apt-get install -y openssl

	cd $FIREFLY_ROOT
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

cd $FIREFLY_ROOT

if [ -d "$FIREFLY_ROOT/Serenity" ]; then
	cd $FIREFLY_ROOT/Serenity
	git pull
else
	git clone https://github.com/zpriddy/Serenity.git
fi

sudo cp $FIREFLY_ROOT/Serenity/serenity.config $FIREFLY_ROOT/config

sudo pip install -r $FIREFLY_ROOT/Serenity/requirements.txt

sed "s/<<DOMAIN>>/$DOMAIN/" $FIREFLY_ROOT/Serenity/nginx.confg > /etc/nginx/sites-enabled/default

##################################
# INSTALL AUTO-START SCRIPTS [TODO]
##################################

# Need to verify permissions of serial port
# Need to start Firefly on boot
# Need to start Serenity on boot
# Need to start ha-bridge on boot
echo -e "\n\nSetting Firefly to start on boot.\n\n"
cd $FIREFLY_ROOT/Firefly
cp firefly_startup.sh $FIREFLY_ROOT
cd $FIREFLY_ROOT
chmod +x firefly_startup.sh
(sudo crontab -l; echo -e "@reboot /opt/firefly_system/firefly_startup.sh &") | crontab -


cp $FIREFLY_ROOT/Firefly/system_scripts/firefly.service /lib/systemd/system
chmod 644 /lib/systemd/system/firefly.service
sudo systemctl daemon-reload
sudo systemctl enable firefly.service

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
# COPY CONFIG FILES
# on updates it will only copy *.sample.*
##################################

git config --global user.email $GIT_EMAIL
git config --global user.name $GIT_NAME

cp -r $FIREFLY_ROOT/Firefly/setup_files/config/* $FIREFLY_ROOT/config/

# copy the update script for easy updates
cp $FIREFLY_ROOT/Firefly/system_scripts/update_firefly.sh $FIREFLY_ROOT

##################################
# CREATE PLACE FOR AUDIO FILES
# This is where sound clips go for casting.
##################################

mkdir /var/www/firefly_www/audio
chown -R www-data:www-data /var/www/firefly_www/audio
chmod -R 777 /var/www/firefly_www/audio



##################################
# CLEANUP
##################################

mkdir $FIREFLY_ROOT/logs

echo -e -n "/opt/firefly_system/logs/firefly.log {\n\tsize 100M\n\tcreate 766 root root\n\trotate 5\n}" >> /etc/logrotate.conf

echo "a-0.0.2" > $FIREFLY_ROOT/.firefly.version

chown -R firefly:firefly /opt/firefly_system

# reboot to finish setup
if ask "Would you like to reboot now?" Y; then
	sudo reboot
fi