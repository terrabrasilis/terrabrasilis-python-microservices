#!/bin/bash
## THE ENV VARS ARE NOT READED INSIDE A SHELL SCRIPT THAT RUNS IN CRON TASKS.
## SO, WE WRITE INSIDE THE /etc/environment FILE AND READS BEFORE RUN THE SCRIPT.
echo "export POSTGRES_USER_FILE=\"$POSTGRES_USER_FILE\"" >> /etc/environment
echo "export POSTGRES_PASS_FILE=\"$POSTGRES_PASS_FILE\"" >> /etc/environment
echo "export FTP_USER=\"$FTP_USER\"" >> /etc/environment
echo "export FTP_PASS=\"$FTP_PASS\"" >> /etc/environment
echo "export DOCKER_ENV=$DOCKER_ENV" >> /etc/environment
# run cron in foreground
cron -f