# Docker for raster-publisher:

Define the environment to runs the autonomous job via cron.

This service performs the publication of images on the GeoServer as a layer.

## Cron job

Use the publisher-schedule.cron to define the start time the job.

The default is: every hour and 5, 25 and 45 minutes

## Build the docker image

To build image for this dockerfile use this command:

```bash
# use script to build
cd raster-publisher-env/
./docker-build.sh

# or use the command
docker build -t terrabrasilis/raster-publisher:<version> -f raster-publisher-env/Dockerfile .
```

When use the script docker-build.sh to build, change the desired image version in raster-publisher/COMPONENT_VERSION file.

## Run the docker

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/raster-publisher:<version> sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name raster-publisher -v $PWD/raster-publisher/data:/usr/local/data terrabrasilis/raster-publisher:<version>
```

## Run using compose

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f raster-publisher-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f raster-publisher-env/docker-compose.yml up -d
```