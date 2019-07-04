#svn export https://github.gatech.edu/llerner3/vip/branches/spring2019/brewery/BrewMenu --force
#/usr/bin/python3 BrewMenu/setup.py
if nc -dzw1 github.com 443 && echo |openssl s_client -connect github.com:443 2>&1 |awk '
  handshake && $1 == "Verification" { if ($2=="OK") exit; exit 1 }
  $1 $2 == "SSLhandshake" { handshake = 1 }'
then
  echo "we have connectivity..."
  if [ -d "/home/halfway/BrewMenu" ]; then
	rm -rf /home/halfway/BrewMenu
  fi
  sudo -u halfway git clone https://github.com/VicerExciser/BrewMenu.git
  sleep 3
else
  echo "github host unreachable: update BrewMenu was unsuccessful."
fi

# chmod -R a+wrx /home/halfway/BrewMenu/
# chown -R halfway /home/halfway/BrewMenu/
# chgrp -R users /home/halfway/BrewMenu/

