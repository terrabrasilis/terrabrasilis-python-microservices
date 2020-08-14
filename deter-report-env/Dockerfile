# To build image for this dockerfile use this command:
#   docker build --no-cache -t terrabrasilis/deter-report:<version> -f deter-report-env/Dockerfile .
#
# To run without compose but with shell terminal use this command:
#   docker run --rm --name terrabrasilis_deter_report -v $PWD/deter-report/data:/usr/local/data -it terrabrasilis/deter-report:<version> sh
#
# To run without compose and without shell terminal use this command:
#   docker run -d --rm --name terrabrasilis_deter_report -v $PWD/deter-report/data:/usr/local/data terrabrasilis/deter-report:<version>
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

ARG VERSION="1.0.0"

LABEL "br.inpe.dpi"="INPE/DPI-TerraBrasilis"
LABEL br.inpe.dpi.terrabrasilis="microservice"
LABEL version=${VERSION}
LABEL author="Andre Carvalho"
LABEL author.email="andre.carvalho@inpe.br"
LABEL description="This microservice provides a task to reads data from publish database and send an e-mail with report \
the new areas of deforestation and degradation, runs only autonomous job via cron."

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

# INSTALL DETER REPORT SERVICE
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/deter-report
COPY deter-report/ $INSTALL_PATH/deter-report/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/deter-report/config/requirements.txt
# END DETER REPORT SERVICE
# ------------------------------------------------------

# install and enable cron job scripts
ADD deter-report-env/cron_exec.sh $INSTALL_PATH/
RUN chmod +x /usr/local/cron_exec.sh
ADD deter-report-env/dailyharvesting.cron /etc/crontabs/root
RUN chmod +x /etc/crontabs/root

ENV DOCKER_ENV True

VOLUME ["/usr/local/data/"]

WORKDIR $INSTALL_PATH

CMD crond -l 2 -f