# Docker for raster-process:

Define the environment to runs the autonomous job via cron.

This service performs the process of converting raster images.

## Cron job
Use the process-schedule.cron to define the start time the job.

The default is: every hour and 10, 30 and 50 minutes

## Build the docker image

To build image for this dockerfile use this command:

```bash
# use script to build
cd raster-process-env/
./docker-build.sh

# or use the command
docker build -t terrabrasilis/raster-process:<version> -f raster-process-env/Dockerfile .
```

When use the script docker-build.sh to build, change the desired image version in raster-process/COMPONENT_VERSION file.

## Run the docker

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/raster-process:v0.1 sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name raster-process -v $PWD/raster-process/data:/usr/local/data terrabrasilis/raster-process:v0.1
```

## Run using compose

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f raster-process-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f raster-process-env/docker-compose.yml up -d
```