# Docker for raster-ftp-download:

Define the environment to runs the autonomous job via cron.

This service downloads raster images from the FTP server.

## Cron job

Use the ftp-schedule.cron to define the start time the job.

The default is: every hour and 0, 20 and 40 minutes

## Build the docker image

To build image for this dockerfile use this command:

```bash
# use script to build
cd raster-ftp-download-env/
./docker-build.sh

# or use the command
docker build -t terrabrasilis/raster-ftp-download:<version> -f raster-ftp-download-env/Dockerfile .
```

When use the script docker-build.sh to build, change the desired image version in raster-ftp-download/COMPONENT_VERSION file.

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/raster-ftp-download:<version> sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name raster-ftp-download -v $PWD/raster-ftp-download/data:/usr/local/data terrabrasilis/raster-ftp-download:<version>
```

## Run using compose

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f raster-ftp-download-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f raster-ftp-download-env/docker-compose.yml up -d
```