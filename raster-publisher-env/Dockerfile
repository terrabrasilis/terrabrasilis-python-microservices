# To build image for this dockerfile use this command:
#   docker build -t terrabrasilis/raster-publisher:<tag-version> -f raster-publisher-env/Dockerfile .
#
# To run without compose but with shell terminal use this command:
#   docker run --rm --name raster-publisher -v $PWD/raster-publisher/data:/usr/local/data -it terrabrasilis/raster-publisher:<tag-version> sh
#
# To run without compose and without shell terminal use this command:
#   docker run -d --rm --name raster-publisher -v $PWD/raster-publisher/data:/usr/local/data terrabrasilis/raster-publisher:<tag-version>
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
FROM python:3.6-alpine

ARG VERSION="1.0.0"

LABEL "br.inpe.dpi"="INPE/DPI-TerraBrasilis"
LABEL br.inpe.dpi.terrabrasilis="microservice"
LABEL version=${VERSION}
LABEL author="Jether Rodrigues"
LABEL author.email="jetherrodrigues@gmail.com"
LABEL collaborator="Andre Carvalho"
LABEL collaborator.email="andre.carvalho@inpe.br"
LABEL description="This microservice lists all * .tif files in the processed folder \
and publishes these rasters to the Geoserver using the Geoserver REST API. \
No ports are exposed, runs only autonomous job via cron."

# define the install path env var
ENV INSTALL_PATH /usr/local

ENV PYTHONUNBUFFERED 1
#-------------Application Specific Stuff ----------------------------------------------------

RUN apk update \
  && apk add --no-cache --update \
    curl \
    tzdata \
    && rm -rf /var/cache/apk/*

# define the timezone to run cron
ENV TZ=America/Sao_Paulo
#---------------------------------------------------------------------------------------------
# INSTALL COMMON MODULES
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/common_modules
COPY common_modules/ $INSTALL_PATH/common_modules/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/common_modules/configuration/config/requirements.txt
# END COMMON MODULES INSTALATION
# ------------------------------------------------------

# INSTALL raster-publisher SERVICE
# ------------------------------------------------------
RUN mkdir -p $INSTALL_PATH/raster-publisher
COPY raster-publisher/ $INSTALL_PATH/raster-publisher/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/raster-publisher/config/requirements.txt
# END raster-publisher SERVICE
# ------------------------------------------------------

# install and enable cron job scripts
ADD raster-publisher-env/cron_exec.sh $INSTALL_PATH/
ADD raster-publisher-env/publisher-schedule.cron /etc/crontabs/root
RUN chmod +x /usr/local/cron_exec.sh \
&& chmod +x /etc/crontabs/root

# 
ENV DOCKER_ENV True

RUN mkdir -p /geoserver/storage/data

VOLUME ["/usr/local/data", "/usr/local/data/processed", "/usr/local/data/config", "/geoserver/storage/data"]

WORKDIR $INSTALL_PATH

CMD crond -l 2 -f