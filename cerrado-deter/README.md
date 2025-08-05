# intersection service
The purpose of this service reads the most recent data from DETER Cerrado production table and write them in one output table to DETER Cerrado publish table.

## The input
The input data is the alerts features detected from CBERS 4 images by the DETER project.

## The configuration
The configurations is stored in the files at src/config directory. It's three files, one to databases connection parameters, another to parameters of the email and the last to adjust the prefixes and sufixes of input and output tables.

Use the example config files for create your own configurations.
Change the extension for each .cfg.example file to .cfg and type your values.
Caution: Do not change the keys and session names only the values.

### SQLView to copy data

```sql
-- DROP VIEW public.production_alert;

CREATE OR REPLACE VIEW public.production_alert
 AS
 SELECT remote_data.gid,
    remote_data.cell_oid,
    remote_data.uuid,
    remote_data.path_row,
    remote_data.sensor,
    remote_data.satellite,
    remote_data.class_name,
    remote_data.area_km,
    remote_data.view_date,
    remote_data.created_date,
    remote_data.audited_date,
    remote_data.geom
   FROM dblink('hostaddr=<host> port=5432 dbname=DeterCerrado user=<user> password=<password>'::text,
   'SELECT object_id as gid, cell_oid, uuid::text, path_row, sensor, satellite, class_name, area as area_km, view_date, created_date, audited_date, spatial_data as geom FROM public.alertas'::text)
   remote_data(gid integer, cell_oid character varying(254), uuid text, path_row character varying(100), sensor character varying(100), satellite character varying(255), class_name character varying(254), area_km double precision, view_date date, created_date date, audited_date date, geom geometry(Polygon,4674));

```

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
