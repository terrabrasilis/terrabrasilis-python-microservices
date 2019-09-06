# intersection service
The purpose of this service reads the most recent data from DETER Cerrado production table and write them in one output table to DETER Cerrado publish table.

## The input
The input data is the alerts features detected from CBERS 4 images by the DETER project.

## The configuration
The configurations is stored in the files at src/config directory. It's three files, one to databases connection parameters, another to parameters of the email and the last to adjust the prefixes and sufixes of input and output tables.

Use the example config files for create your own configurations.
Change the extension for each .cfg.example file to .cfg and type your values.
Caution: Do not change the keys and session names only the values.

## The code
This service is written in Python 3 and its dependencies is defined in requirements.txt file at config directory.

## Local for devel
For developer we recommend the Visual Studio Code and python virtual environment.
Before proceed, follow the instructions of the README file on the root directory of the main project.
After that, follow the session "The configuration" above.

## Docker for production
Go to the home project path and run the command to start container.

Warning: In production mode the configuration module will read the config files at /usr/local/data/config directory using the absolute path defined as volume in Dockerfile. So, go to the external volume location and define your own config files inside a directory named config. See the instructions on the "The configuration" session.

```sh
docker-compose -f cerrado-deter-environment/docker-compose.yml up -d
```
