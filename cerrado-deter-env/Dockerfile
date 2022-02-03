# WARNING - Read before proceeding
# Before creating a new image, remember to change the version by creating a new tag to indicate
# the new version of the image.
# If you do not change, the generated image will replace the old one in the docker registry.
# To create an image for this dockerfile, use the docker_build.sh script.
#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM python:3.5.10-alpine

ARG VERSION="1.0.0"

LABEL "br.inpe.dpi"="INPE/DPI-TerraBrasilis"
LABEL br.inpe.dpi.terrabrasilis="microservice"
LABEL version=${VERSION}
LABEL author="Andre Carvalho"
LABEL author.email="andre.carvalho@inpe.br"
LABEL description="This microservice provides a harvesting to get the alerts \
of deforestation from production DETER cerrado database, intersects them with \
interest areas and write the resultant data in publish database. \
No ports are exposed, runs only autonomous job via cron."

ENV PYTHONUNBUFFERED 1
#-------------Application Specific Stuff ----------------------------------------------------

RUN apk update \
  && apk add --no-cache --update \
    build-base \
    postgresql \
    postgresql-dev \
    libpq \
    tzdata \
    libxslt-dev \
    libxml2-dev \
    && rm -rf /var/cache/apk/*

ENV TZ=America/Sao_Paulo
ENV LIBRARY_PATH=/lib:/usr/lib
# define the install path env var
ENV INSTALL_PATH /usr/local

# Install Python requirements
# ------------------------------------------------------
ADD common_modules/configuration/config/requirements.txt ${INSTALL_PATH}/common_modules/configuration/config/
ADD common_modules/postgresql/config/requirements.txt ${INSTALL_PATH}/common_modules/postgresql/config/
ADD cerrado-deter/config/requirements.txt ${INSTALL_PATH}/cerrado-deter/config/
RUN pip install -r ${INSTALL_PATH}/common_modules/configuration/config/requirements.txt \
&& pip install -r ${INSTALL_PATH}/common_modules/postgresql/config/requirements.txt \
&& pip install -r ${INSTALL_PATH}/cerrado-deter/config/requirements.txt


# INSTALL COMMON MODULES
# ------------------------------------------------------
COPY common_modules/ ${INSTALL_PATH}/common_modules/
COPY cerrado-deter/ ${INSTALL_PATH}/cerrado-deter/

# install and enable cron job scripts
ADD cerrado-deter-env/cron_exec.sh ${INSTALL_PATH}/
ADD cerrado-deter-env/dailyharvesting.cron /etc/crontabs/root
RUN chmod +x ${INSTALL_PATH}/cron_exec.sh \
&& chmod +x /etc/crontabs/root

ENV DOCKER_ENV True

VOLUME ["${INSTALL_PATH}/data"]

WORKDIR ${INSTALL_PATH}

CMD crond -l 2 -f