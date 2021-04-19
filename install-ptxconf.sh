#!/bin/bash

# File:	install-ptxconf.sh
# Author:	Charlie Martínez® <cmartinez@quirinux.org>
# License:	https://www.gnu.org/licenses/gpl-3.0.txt
# Description:	PTXConf Debian Buster Installer
# Version:	1.00-Beta

clear

echo " -----------------------------------------------------------------------------
 PTXCONF DEBIAN BUSTER INSTALLER
 -----------------------------------------------------------------------------
 Ptxconf is a utility programmed by wenhsinjen, which is used to map a 
 graphics tablet to a single monitor when using more than one. Manages 
 graphically the xorg map-to-input command and is very useful under the 
 xfce desktop, default in Quirinux.
 1 Install Ptxconf (recommended if you use XFCE)
 0 Quit
"

read -p " Your answer-> " opc 

case $opc in

"1") 

clear

# INSTALL PTXCONF UTILITY (MAPPING)

sudo mkdir -p /opt/tmp/ptxtemp
sudo wget  --no-check-certificate 'http://my.opendesktop.org/s/ajaj7dRJFp8PJFK/download' -O /opt/tmp/ptxtemp/ptxconf.tar
sudo tar -xf /opt/tmp/ptxtemp/ptxconf.tar -C /opt/
cd /opt/ptxconf
sudo python setup.py install
sudo apt-get install -f -y
sudo apt-get install libappindicator1
sudo mkdir -p /opt/tmp/python-appindicator
sudo wget  --no-check-certificate 'http://my.opendesktop.org/s/gfCdMmfLaX627rj/download' -O /opt/tmp/python-appindicator/python-appindicator_0.4.92-4_amd64.deb
sudo dpkg -i /opt/tmp/python-appindicator/python-appindicator_0.4.92-4_amd64.deb
sudo apt-get install -f -y
sudo apt-get autoremove --purge -y

# Add entry to start

for usuarios_ptx in /home/*; do sudo yes | sudo cp -r -a /opt/tmp/ptxtemp/.config $usuarios_ptx; done

# Delete temporary files 

sudo rm -rf /opt/tmp/*

clear

echo " -----------------------------------------------------------------------------
 PTXCONF DEBIAN BUSTER INSTALLER
 -----------------------------------------------------------------------------
 Ptxconf is installed. When you restart your computer, 
 it will appear on the taskbar.
"

;;

"0")

clear

exit 0

;; 

esac 

clear
