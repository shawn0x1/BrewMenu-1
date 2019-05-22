#svn export https://github.gatech.edu/llerner3/vip/branches/spring2019/brewery/BrewMenu --force
#/usr/bin/python3 BrewMenu/setup.py
if [ -d "/home/halfway/BrewMenu" ]; then
	rm -rf /home/halfway/BrewMenu
fi
git clone https://github.com/VicerExciser/BrewMenu.git
sleep 3

#mv -f /home/halfway/BrewMenu/BrewMenu/* /home/halfway/BrewMenu/
#rm -rf /home/halfway/BrewMenu/BrewMenu

if [ ! -d "/home/halfway/BrewMenu/ascii_art" ]; then
	mkdir /home/halfway/BrewMenu/ascii_art
fi
chmod a+wrx /home/halfway/BrewMenu/*
chown halfway /home/halfway/BrewMenu/*

/usr/bin/python3 /home/halfway/BrewMenu/setup.py
menu () { cd /home/halfway/BrewMenu; }
menu
