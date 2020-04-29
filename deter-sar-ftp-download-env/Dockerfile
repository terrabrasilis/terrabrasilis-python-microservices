# To build image for this dockerfile use the script: ./docker-build.sh 
# WARNING: Before build one image, check the version on PROJECT_VERSION file and, if needed, change that.
#
# To run without compose but with shell terminal use this command:
#   docker run --rm --name deter-sar-ftp-download -v /tmp:/usr/local/data -it terrabrasilis/deter-sar-ftp-download:<version> sh
#
# To run without compose and without shell terminal use this command:
#   docker run -d --rm --name deter-sar-ftp-download -v /tmp:/usr/local/data terrabrasilis/deter-sar-ftp-download:<version>
# 
# Information from doc of help about run one container without an explicit service. Run in background
# --------------------------------------------------------------------------------
# --rm,                      Tell to docker engine to remove container after container is stopped
# --name,                    Define one name for running container
# -d, --detach=false         Run container in background and print container ID
# -t, --tty=false            Allocate a pseudo-TTY
# --no-cache                 Ignore all cached intermediary layer
# --------------------------------------------------------------------------------
#
#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
#FROM python:3.5.2-alpine
FROM ubuntu:18.04

ARG VERSION="1.0.0"

LABEL "br.inpe.dpi"="INPE/DPI-TerraBrasilis"
LABEL br.inpe.dpi.terrabrasilis="microservice"
LABEL version=${VERSION}
LABEL author="Andre Carvalho"
LABEL author.email="andre.carvalho@inpe.br"
LABEL description="This microservice download the ZIP file from FTP and send to database. \
No ports are exposed, runs only autonomous job via cron."

ENV PYTHONUNBUFFERED 1
#-------------Application Specific Stuff ----------------------------------------------------
RUN apt-get -o Acquire::ForceIPv4=true update \
    && apt-get install -y \
    wget \
    gnupg \
    python3-pip

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get -o Acquire::ForceIPv4=true update \
    && export DEBIAN_FRONTEND="noninteractive" \
    && apt-get install -y --no-install-recommends \
      postgresql-11-postgis-2.5 \
      postgis \
      cron \
      tzdata \
    && rm -rf /var/lib/apt/lists/*

# define the timezone to run cron
ENV TZ=America/Sao_Paulo

# define the install path env var
ENV INSTALL_PATH /usr/local

# INSTALL COMMON MODULES
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/common_modules
COPY common_modules/ $INSTALL_PATH/common_modules/
# Install Python requirements
RUN pip3 install -r $INSTALL_PATH/common_modules/configuration/config/requirements.txt \
&& pip3 install -r $INSTALL_PATH/common_modules/postgresql/config/requirements.txt
# END COMMON MODULES INSTALATION
# ------------------------------------------------------

# INSTALL deter-sar-ftp-download SERVICE
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/deter-sar-ftp-download
COPY deter-sar-ftp-download/ $INSTALL_PATH/deter-sar-ftp-download/
# Install Python requirements
# RUN pip3 install -r $INSTALL_PATH/deter-sar-ftp-download/config/requirements.txt
# END deter-sar-ftp-download SERVICE
# ------------------------------------------------------
# install script to docker entry point
ADD deter-sar-ftp-download-env/docker-entrypoint.sh $INSTALL_PATH/bin/docker-entrypoint.sh
RUN chmod +x $INSTALL_PATH/bin/*.sh \
    && ln -s usr/local/bin/docker-entrypoint.sh / # backwards compat

# install and enable cron job scripts
ADD deter-sar-ftp-download-env/cron_exec.sh $INSTALL_PATH/
RUN chmod +x $INSTALL_PATH/*.sh \
  && chmod +x $INSTALL_PATH/deter-sar-ftp-download/*.sh
# install and enable config cron
# for schedule to download from ftp
ADD deter-sar-ftp-download-env/ftp-schedule.cron /etc/cron.d/ftp-schedule-cron
RUN chmod 0644 /etc/cron.d/ftp-schedule-cron \
    && crontab /etc/cron.d/ftp-schedule-cron 

# to select production configuration
ENV DOCKER_ENV True

VOLUME ["/usr/local/data"]

WORKDIR $INSTALL_PATH

ENTRYPOINT [ "/docker-entrypoint.sh" ]