#!/bin/bash
host=$(cat /usr/local/data/config/db.cfg | grep -oP '(?<=host: )[^"]*')
port=$(cat /usr/local/data/config/db.cfg | grep -oP '(?<=port: )[^"]*')
database=$(cat /usr/local/data/config/db.cfg | grep -oP '(?<=dbname: )[^"]*')
OUTPUT_TABLE="deter_sar_1ha"
BASE_DIR="/usr/local/data"
DATE=$(date +"%Y-%m-%d_%H:%M:%S")

export PGUSER=`cat /run/secrets/postgres.user.forest.monitor`
export PGPASSWORD=`cat /run/secrets/postgres.pass.forest.monitor`
#export PGPASSWORD="postgres"

PG_BIN="/usr/bin"
PG_CON="-d $database -p $port -h $host"

# Define SQL to log the success operation. Tips to select datetime as a string (to_char(timezone('America/Sao_Paulo',imported_at),'YYYY-MM-DD HH24:MI:SS'))
LOG_IMPORT="INSERT INTO public.deter_sar_import_log(imported_at, filename) VALUES (timezone('America/Sao_Paulo',now()), '$SHP_NAME')"

#SQL="DROP TABLE IF EXISTS public.deter_sar_1ha"
#$PG_BIN/psql $PG_CON -t -c "$SQL"

#PROJ4=`gdalsrsinfo -o proj4 $SHP_NAME_AND_DIR`
# find the EPSG code to reproject
#SQL="SELECT srid FROM public.spatial_ref_sys WHERE proj4text = $PROJ4"
#EPSG=($($PG_BIN/psql $PG_CON -t -c "$SQL"))

# default srid
EPSG=4326
# Options to New table mode
#SHP2PGSQL_OPTIONS="-c -s $EPSG:4326 -W 'LATIN1' -g geometries"
# Options to Append mode
SHP2PGSQL_OPTIONS="-a -s $EPSG:4326 -W 'LATIN1' -g geometries"

# import shapefiles
if $PG_BIN/shp2pgsql $SHP2PGSQL_OPTIONS $BASE_DIR"/"$SHP_NAME $OUTPUT_TABLE | $PG_BIN/psql $PG_CON
then
    echo "$DATE - Import ($SHP_NAME) ... OK" >> $BASE_DIR"/log/import-shapefile.log"
    rm $BASE_DIR"/shpname.txt"
    $PG_BIN/psql $PG_CON -t -c "$LOG_IMPORT"
else
    echo "$DATE - Import ($SHP_NAME) ... FAIL" >> $BASE_DIR"/log/import-shapefile.log"
fi

# if we need to transform the Julian day to Gregoria date and time use this query
# select dt,TO_CHAR( (dc::text)::interval, 'HH24:MI:SS') FROM (
# 	SELECT to_date((2458940 - FLOOR(daydetect_))::text, 'J') as dt, (daydetect_ % 1)*86400 as dc
# 	FROM public.deter_sar_1ha limit 10
# ) as tb