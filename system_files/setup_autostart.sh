#! /bin/bash

FIREFLY_ROOT="/opt/firefly_system"

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

##################################
# INSTALL AUTO-START SCRIPTS
##################################

cp $FIREFLY_ROOT/Firefly/system_files/firefly.service /lib/systemd/system
chmod 644 /lib/systemd/system/firefly.service
sudo systemctl daemon-reload
sudo systemctl enable firefly.service

cp $FIREFLY_ROOT/Firefly/system_files/ffbeacon.service /lib/systemd/system
chmod 644 /lib/systemd/system/ffbeacon.service
chmod +x $FIREFLY_ROOT/Firefly/system_files/firefly_beacon.sh
sudo systemctl daemon-reload
sudo systemctl enable ffbeacon.service


##################################
# SETUP LOGS FOR FIREFLY
##################################

mkdir $FIREFLY_ROOT/logs
chmod -R 775 $FIREFLY_ROOT/logs

echo -e -n "/opt/firefly_system/logs/firefly.log {\n\tsize 100M\n\tcreate 766 root root\n\trotate 5\n}" >> /etc/logrotate.conf
echo -e -n "/opt/firefly_system/logs/firefly_beacon.log {\n\tsize 100M\n\tcreate 766 root root\n\trotate 5\n}" >> /etc/logrotate.conf
echo -e -n "/opt/firefly_system/logs/firefly_update.log {\n\tsize 100M\n\tcreate 766 root root\n\trotate 5\n}" >> /etc/logrotate.conf
echo -e -n "/opt/firefly_system/logs/firefly_brakeglass.log {\n\tsize 100M\n\tcreate 766 root root\n\trotate 5\n}" >> /etc/logrotate.conf

#################################
# SETUP CRON FOR FUTURE UPDATES
#################################
#write out current crontab
cd $FIREFLY_ROOT/Firefly/system_files
sudo crontab -l > mycron
#echo new cron into cron file
echo "SHELL=/bin/sh" >> mycron
echo "MAILTO=/var/mail/root" >> mycron
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games" >> mycron
echo "" >> mycron
echo "00 02 * * 6 /opt/firefly_system/Firefly/system_files/update_firefly.sh >> /opt/firefly_system/logs/firefly_update.log" >> mycron
echo "00 * * * * /opt/firefly_system/Firefly/system_files/update_scripts/firefly_brakeglass_update.sh >> /opt/firefly_system/logs/firefly_brakeglass.log" >> mycron
echo "" >> mycron
#install new cron file
sudo crontab mycron
rm mycron

chmod +x /opt/firefly_system/Firefly/system_files/update_firefly.sh
chmod +x /opt/firefly_system/Firefly/system_files/restart_firefly.sh
bash /opt/firefly_system/Firefly/system_files/update_firefly.sh


# reboot to finish setup
if ask "Would you like to reboot now? Firefly should launch on boot." Y; then
	sudo reboot
fi