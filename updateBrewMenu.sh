#svn export https://github.gatech.edu/llerner3/vip/branches/spring2019/brewery/BrewMenu --force
#/usr/bin/python3 BrewMenu/setup.py
if [ -d "/home/halfway/BrewMenu" ]; then
	rm -rf /home/halfway/BrewMenu
fi
sudo -u halfway git clone https://github.com/VicerExciser/BrewMenu.git
sleep 3


# chmod -R a+wrx /home/halfway/BrewMenu/
# chown -R halfway /home/halfway/BrewMenu/
# chgrp -R users /home/halfway/BrewMenu/

