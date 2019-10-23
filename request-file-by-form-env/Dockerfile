# To build image for this dockerfile use this command:
#   docker build -t terrabrasilis/request-file-by-form:v0.1 -f request-file-by-form-env/Dockerfile .
#
# To run without compose and without shell terminal use this command:
#   docker run -d --rm --name terrabrasilis_request_file \
#   -p 7000:7000 --env POSTGRES_PASS_FILE=<secret_password> \
#   --env SMTP_INPE_MAIL_USER_FILE=<email_from> \
#   --env SMTP_INPE_MAIL_PASS_FILE=<secret_password> \
#   -v $PWD/request-file-by-form/src/config:/usr/local/data/config \
#   terrabrasilis/request-file-by-form:v0.1
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
LABEL br.inpe.dpi.terrabrasilis="app"
LABEL version="v0.1"
LABEL author="Andre Carvalho"
LABEL author.email="andre.carvalho@inpe.br"
LABEL description="This app provides a service to store some user data, one form to input user data and one service to send email with download link."

ENV PYTHONUNBUFFERED 1
#-------------Application Specific Stuff ----------------------------------------------------

RUN apk update \
  && apk add --no-cache --update \
    build-base \
    postgresql \
    postgresql-dev \
    libpq \
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

# INSTALL APP
# ------------------------------------------------------
RUN mkdir $INSTALL_PATH/request-file-by-form
COPY request-file-by-form/ $INSTALL_PATH/request-file-by-form/
# Install Python requirements
RUN pip install -r $INSTALL_PATH/request-file-by-form/config/requirements.txt
# END APP
# ------------------------------------------------------

ENV DOCKER_ENV True

VOLUME ["/usr/local/data/config"]

EXPOSE 7000

WORKDIR $INSTALL_PATH/request-file-by-form/src

# using the gunicorn as a WSGI server
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:7000", "wsgi:app"]