# To build image for this dockerfile use this command:
#   docker build -t terrabrasilis/raster-ftp-download:v0.2 -f raster-ftp-download-env/Dockerfile .
#
# To run without compose but with shell terminal use this command:
#   docker run --rm --name raster-ftp-download -v $PWD/raster-ftp-download/data:/usr/local/data -it terrabrasilis/raster-ftp-download:v0.2 sh
#
# To run without compose and without shell terminal use this command:
#   docker run -d --rm --name raster-ftp-download -v $PWD/raster-ftp-download/data:/usr/local/data terrabrasilis/raster-ftp-download:v0.2
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
FROM python:3.5.2-alpine

LABEL "br.inpe.dpi"="INPE/DPI-TerraBrasilis"
LABEL br.inpe.dpi.terrabrasilis="microservice"
LABEL version="0.2"
LABEL author="Jether Rodrigues"
LABEL author.email="jetherrodrigues@gmail.com"
LABEL description="This microservice execute the FTP images download and store them into a folder. \
No ports are exposed, runs only autonomous job via cron."

ENV PYTHONUNBUFFERED 1
#-------------Application Specific Stuff ----------------------------------------------------

RUN apk update \
  && apk add --no-cache --update \
    build-base \
    postgresql \
    postgresql-dev \
    libpq \
    libxslt-dev \
    libxml2-dev \
    tzdata

# define the timezone to run cron
ENV TZ=America/Sao_Paulo

# define the install path env var
ENV INSTALL_PATH /usr/local

# INSTALL COMMON MODULES
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/common_modules
COPY common_modules/ $INSTALL_PATH/common_modules/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/common_modules/configuration/config/requirements.txt && \
pip install -r $INSTALL_PATH/common_modules/postgresql/config/requirements.txt
# END COMMON MODULES INSTALATION
# ------------------------------------------------------

# INSTALL raster-ftp-download SERVICE
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/raster-ftp-download
COPY raster-ftp-download/ $INSTALL_PATH/raster-ftp-download/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/raster-ftp-download/config/requirements.txt
# END raster-ftp-download SERVICE
# ------------------------------------------------------

# install and enable cron job scripts
ADD raster-ftp-download-env/cron_exec.sh $INSTALL_PATH/
RUN chmod +x /usr/local/cron_exec.sh
ADD raster-ftp-download-env/ftp-schedule.cron /etc/crontabs/root
RUN chmod +x /etc/crontabs/root

# 
ENV DOCKER_ENV True

VOLUME ["/usr/local/data", "/usr/local/data/config"]

WORKDIR $INSTALL_PATH

CMD crond -l 2 -f