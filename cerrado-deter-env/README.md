# Docker for DETER-CERRADO data synchronization

Define the environment to runs the autonomous job via cron.

This service load data from production database, intersect them with interest areas and write in publish database.


## Cron job
Use the dailyharvesting.cron to define the start time the job.

## Run the docker

To build image for this dockerfile use this command:

```bash
docker build -t terrabrasilis/cerradodeter-syncdata:<version> -f cerrado-deter-env/Dockerfile .
```

To run without compose but with shell terminal, use this command:

```bash
docker run -it terrabrasilis/cerradodeter-syncdata:<version> sh
```


To run without compose and without shell terminal use this command:

```bash
docker run -d --rm --name terrabrasilis_deter_cerrado -v /tmp/cerrado-deter:/usr/local/data terrabrasilis/cerradodeter-syncdata:<version>
```

## Run using compose

Change the docker image version on docker-compose.yml file before run.

Are two ways for run this service using docker-compose.

### To run in atached mode

```bash
docker-compose -f cerrado-deter-env/docker-compose.yml up
```

### To run in detached mode

```bash
docker-compose -f cerrado-deter-env/docker-compose.yml up -d
```