# Docker for DETER-AMZ data report

Define the environment to runs the autonomous job via cron.

This service reads publish database to send e-mail with a report about new data that will publishing.


## Cron job
Use the dailyharvesting.cron to define the start time the job.

## Run the docker

To build image for this dockerfile use this command:

```bash
docker build -t terrabrasilis/deter-report:v0.3 -f deter-report-env/Dockerfile .
```

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/deter-report:v0.3 sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name terrabrasilis_deter_report -v /tmp/deter-report:/usr/local/data terrabrasilis/deter-report:v0.3
```

## Run using compose

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f deter-report-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f deter-report-env/docker-compose.yml up -d
```