# Docker for deter-ftp-download:

Define the environment to runs the autonomous job via cron.

For DETER AMZ and DETER CERRADO.

This service do DETER backup download from FTP server, drops the current table and create a new one using the downloaded data file.

See in portainer the ["deterb_data_sync" Stack](http://terrabrasilis.dpi.inpe.br/portainer/#/stacks/deterb_data_sync?id=19&type=1&external=false) where this service is running.

## Cron job

Use the ftp-schedule.cron to define the start time the job.

## Run the docker

To build image for this dockerfile use this command:

```bash
docker build -t terrabrasilis/deter-ftp-download:v0.2 -f deter-ftp-download-env/Dockerfile .
```

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/deter-ftp-download:v0.2 sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name deter-ftp-download -v $PWD/deter-ftp-download/data:/usr/local/data terrabrasilis/deter-ftp-download:v0.2
```

## Run using compose

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f deter-ftp-download-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f deter-ftp-download-env/docker-compose.yml up -d
```