# Docker for raster-process:

Define the environment to runs the autonomous job via cron.

This service execute the raster images process.

## Cron job
Use the process-schedule.cron to define the start time the job.

## Run the docker

To build image for this dockerfile use this command:

```bash
docker build -t terrabrasilis/raster-process:v0.1 -f raster-process-env/Dockerfile .
```

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