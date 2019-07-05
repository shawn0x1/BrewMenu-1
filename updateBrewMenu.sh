#!/bin/bash
sleep 3
if nc -dzw1 github.com 443 && echo |openssl s_client -connect github.com:443 2>&1 |awk '
  handshake && $1 == "Verification" { if ($2=="OK") exit; exit 1 }
  $1 $2 == "SSLhandshake" { handshake = 1 }'
then
  echo "[ We have connectivity... ]"
  if [ -d "/home/halfway/BrewMenu" ]; then
	rm -rf /home/halfway/BrewMenu
  fi
  git clone https://github.com/VicerExciser/BrewMenu.git
  sleep 3
else
  echo "[[<ERROR :: GitHub host unreachable: Update BrewMenu was unsuccessful.>]]"
fi
