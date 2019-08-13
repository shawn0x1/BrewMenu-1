import os
from subprocess import call
import sys
import stat

os.system('echo "set tabsize 4" > /home/halfway/.nanorc')
# os.system('echo "set tabstospaces" >> /home/halfway/.nanorc')

prefix_fp='/home/halfway/BrewMenu/'
if os.path.isfile('removelist.txt'):
	with open(prefix_fp+'removelist.txt','r') as rl:
	    for line in rl:
	        if os.path.isfile(prefix_fp+line):
	            os.system("rm %s%s" % (prefix_fp,line))
os.system("rm "+prefix_fp+"removelist.txt")
os.system('echo "deb http://mirror.us.leaseweb.net/raspbian/raspbian/ stretch main contrib non-free rpi firmware" > /etc/apt/sources.list')
os.system("apt update")
prefix_apt="apt-get install -yq --show-progress "
prefix_pip="pip install -q "
prefix_pip3="pip3 install -q "
prefix_ei="easy_install --upgrade "

apt_packages=[
	"python3-setuptools",
	"python-pip",
	"python3-pip",
	"git",
	#"python-dev",
	"build-essential",
	# "xterm",
	"toilet",
	"fbi",
	"fim",
	# "imagemagick",
	"subversion",
	"libjpeg-dev",
	"figlet"
]
pip_packages=[
	"pyasn1==0.4.1",
	"google-api-python-client",
	"google-auth-httplib2",
	"google-auth-oauthlib",
	"pillow==2.7.0",			## FIXME: PROBLEM INSTALLING PILLOW
	"asciimatics",
	"pyyaml"
]

pkgstr=""
for pkg in apt_packages:
	pkgstr+="{} ".format(pkg)
os.system("{}{}".format(prefix_apt,pkgstr))

pkgstr=""
for pkg in pip_packages:
	pkgstr+="{} ".format(pkg)
	call(prefix_pip + pkg, shell=True)
	call(prefix_pip3 + pkg, shell=True)
# os.system("{}{}".format(prefix_pip,pkgstr))
# os.system("{}{}".format(prefix_pip3,pkgstr))
os.system("{}{}".format(prefix_ei,pkgstr))

# os.system('echo "/usr/bin/python3 /home/halfway/BrewMenu/brewmenu.py" > brewmenu')
# os.chmod('brewmenu',stat.S_IEXEC|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)
# os.system('ln -s brewmenu /usr/local/bin')
# os.system('. brewmenu')
