#!/bin/sh
source /etc/environment
/usr/bin/python3 /usr/local/deter-sar-ftp-download/src/main.py

if [ -f "/usr/local/data/shpname.txt" ];
then
	export SHP_NAME=`cat /usr/local/data/shpname.txt`
  /bin/sh /usr/local/deter-sar-ftp-download/update-database.sh
  /bin/sh /usr/local/deter-sar-ftp-download/clean-old-files.sh
else
  #The parameter SHP_NAME is empty!
	exit
fi;
