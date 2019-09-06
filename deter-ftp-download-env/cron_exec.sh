#!/bin/sh
/usr/local/bin/python3 /usr/local/deter-ftp-download/src/main.py

/bin/sh /usr/local/deter-ftp-download/update-amz.sh
/bin/sh /usr/local/deter-ftp-download/update-cerrado.sh