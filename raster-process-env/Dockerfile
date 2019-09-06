# To build image for this dockerfile use this command:
#   docker build -t terrabrasilis/raster-process:v0.1 -f raster-process-env/Dockerfile .
#
# To run without compose but with shell terminal use this command:
#   docker run --rm --name raster-process -v $PWD/raster-process/data:/usr/local/data -it terrabrasilis/raster-process:v0.1 sh
#
# To run without compose and without shell terminal use this command:
#   docker run -d --rm --name raster-process -v $PWD/raster-process/data:/usr/local/data terrabrasilis/raster-process:v0.1
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

LABEL "br.inpe.dpi"="INPE/DPI-TerraBrasilis"
LABEL br.inpe.dpi.terrabrasilis="microservice"
LABEL version="0.1"
LABEL author="Jether Rodrigues"
LABEL author.email="jetherrodrigues@gmail.com"
LABEL description="This microservice list all *.tif files on processed folder and execte gdal_translate cmd. \
No ports are exposed, runs only autonomous job via cron."

# define the install path env var
ENV INSTALL_PATH /usr/local
ENV GDAL_VERSION=v2.2.4
ENV LIBKML_VERSION=1.3.0

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
#---------------------------------------------------------------------------------------------

#--------------------------- Install GDAL ----------------------------------------------------
RUN \
  apk update && \
  apk add --virtual build-dependencies \
    # to reach GitHub's https
    openssl ca-certificates \
    build-base cmake musl-dev linux-headers \
    # for libkml compilation
    zlib-dev minizip-dev expat-dev uriparser-dev boost-dev && \
  apk add \
    # libkml runtime
    zlib minizip expat uriparser boost && \
  update-ca-certificates && \
  mkdir /build && cd /build && \
  apk --update add tar && \
  # libkml
  wget -O libkml.tar.gz "https://github.com/libkml/libkml/archive/${LIBKML_VERSION}.tar.gz" && \
  tar --extract --file libkml.tar.gz && \
  cd libkml-${LIBKML_VERSION} && mkdir build && cd build && cmake .. && make && make install && cd ../.. && \
  # gdal
  wget -O gdal.tar.gz "https://github.com/OSGeo/gdal/archive/${GDAL_VERSION}.tar.gz" && \
  tar --extract --file gdal.tar.gz --strip-components 1 && \
  cd gdal && \
  ./configure --prefix=/usr \
    --with-libkml \
    --without-bsb \
    --without-dwgdirect \
    --without-ecw \
    --without-fme \
    --without-gnm \
    --without-grass \
    --without-grib \
    --without-hdf4 \
    --without-hdf5 \
    --without-idb \
    --without-ingress \
    --without-jasper \
    --without-mrf \
    --without-mrsid \
    --without-netcdf \
    --without-pcdisk \
    --without-pcraster \
    --without-webp \
  && make && make install && \
  # gdal python bindings
  #pip install gdal --no-cache-dir && \
  # cleanup
  apk del build-dependencies && \
  cd / && \
  rm -rf build && \
  rm -rf /var/cache/apk/* && \
  rm -rf /usr/lib/python2.7
#---------------------------------------------------------------------------------------------

# INSTALL COMMON MODULES
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/common_modules
COPY common_modules/ $INSTALL_PATH/common_modules/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/common_modules/configuration/config/requirements.txt && \
pip install -r $INSTALL_PATH/common_modules/postgresql/config/requirements.txt
# END COMMON MODULES INSTALATION
# ------------------------------------------------------

# INSTALL raster-process SERVICE
# ------------------------------------------------------
RUN mkdir -p $INSTALL_PATH/raster-process
COPY raster-process/ $INSTALL_PATH/raster-process/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/raster-process/config/requirements.txt
# END raster-process SERVICE
# ------------------------------------------------------

# install and enable cron job scripts
ADD raster-process-env/cron_exec.sh $INSTALL_PATH/
RUN chmod +x /usr/local/cron_exec.sh
ADD raster-process-env/process-schedule.cron /etc/crontabs/root
RUN chmod +x /etc/crontabs/root

# 
ENV DOCKER_ENV True

VOLUME ["/usr/local/data", "/usr/local/data/processed", "/usr/local/data/config"]

WORKDIR $INSTALL_PATH

CMD crond -l 2 -f