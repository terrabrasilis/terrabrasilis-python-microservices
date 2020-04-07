# Docker for deter-sar-ftp-download:

Define the environment to runs the autonomous job via cron.

For DETER SAR AMZ.

This service do DETER SAR ZIP download from FTP server, drops the current table and create a new one using the downloaded data file.

See in portainer the ["deter_sar_data_sync" Stack](http://terrabrasilis.dpi.inpe.br/portainer/#/stacks/deterb_data_sync?id=19&type=1&external=false) where this service is running.

## Cron job

Use the ftp-schedule.cron to define the start time the job.

## Run the docker

To build image for this dockerfile use this command:

```bash
docker build -t terrabrasilis/deter-sar-ftp-download:<version> -f deter-sar-ftp-download-env/Dockerfile .
```

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/deter-sar-ftp-download:<version> sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name deter-sar-ftp-download -v $PWD/deter-sar-ftp-download/data:/usr/local/data terrabrasilis/deter-sar-ftp-download:<version>
```

## Run using compose

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f deter-sar-ftp-download-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f deter-sar-ftp-download-env/docker-compose.yml up -d
```