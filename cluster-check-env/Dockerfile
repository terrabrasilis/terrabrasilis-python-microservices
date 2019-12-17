# To build image for this dockerfile use this command:
#   docker build -t terrabrasilis/cluster-check:v0.1 -f cluster-check-env/Dockerfile .
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
LABEL version="0.1"
LABEL author="Andre Carvalho"
LABEL author.email="andre.carvalho@inpe.br"
LABEL description="This microservice provide one simple way to check the health of the each cluster node."

ENV PYTHONUNBUFFERED 1
#-------------Application Specific Stuff ----------------------------------------------------

# define the install path env var
ENV INSTALL_PATH /usr/local

# INSTALL cluster-check SERVICE
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/cluster-check
COPY cluster-check/ $INSTALL_PATH/cluster-check/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/cluster-check/config/requirements.txt
# END deter-ftp-download SERVICE
# ------------------------------------------------------

EXPOSE 5000

WORKDIR $INSTALL_PATH/cluster-check/src

# runing server
CMD ["python", "ping_pong.py"]