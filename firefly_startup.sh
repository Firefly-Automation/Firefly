#! /bin/bash

# @Author: Zachary Priddy
# @Date:   2016-12-25 12:31:01
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-12-26 00:43:46

sudo service mongodb start

#cd /opt/firefly_system/Firefly/Firefly
#sudo python run_firefly.py & 
#disown

cd /opt/firefly_system/Serenity/
python runserver.py &
disown

cd /opt/firefly_system
sudo java -jar ha-bridge-3.5.1.jar & 
disown