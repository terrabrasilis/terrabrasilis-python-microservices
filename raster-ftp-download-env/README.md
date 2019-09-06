# Docker for raster-ftp-download:

Define the environment to runs the autonomous job via cron.

This service execute the raster images download from FTP server.

## Cron job
Use the ftp-schedule.cron to define the start time the job.

## Run the docker

To build image for this dockerfile use this command:

```bash
docker build -t terrabrasilis/raster-ftp-download:v0.2 -f raster-ftp-download-env/Dockerfile .
```

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/raster-ftp-download:v0.2 sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name raster-ftp-download -v $PWD/raster-ftp-download/data:/usr/local/data terrabrasilis/raster-ftp-download:v0.2
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