#!/bin/sh

DATA_DIR="/usr/local/data"

INPUT_DETER_TABLE="deter_table.sql"

DATE=$(date +"%Y-%m-%d")

export PGUSER=`cat /run/secrets/postgres.user.deter.amz`
export PGPASSWORD=`cat /run/secrets/postgres.pass.deter.amz`

if ! [ -f $DATA_DIR"/drop_"$INPUT_DETER_TABLE ]
then

    echo "DROP TABLE terrabrasilis.deter_table;" > $DATA_DIR"/drop_"$INPUT_DETER_TABLE

    echo "ALTER TABLE terrabrasilis.deter_table ADD COLUMN publish_month date;" > $DATA_DIR"/createColumnPublishMonth.sql"
    echo "UPDATE terrabrasilis.deter_table " >> $DATA_DIR"/createColumnPublishMonth.sql"
    echo "SET publish_month=overlay(date::varchar placing '01' from 9 for 2)::date;" >> $DATA_DIR"/createColumnPublishMonth.sql"
    echo "CREATE INDEX publish_month_idx " >> $DATA_DIR"/createColumnPublishMonth.sql"
    echo "ON terrabrasilis.deter_table USING btree (publish_month ASC NULLS LAST);" >> $DATA_DIR"/createColumnPublishMonth.sql"
    echo "ALTER TABLE terrabrasilis.deter_table " >> $DATA_DIR"/createColumnPublishMonth.sql"
    echo "CLUSTER ON publish_month_idx;" >> $DATA_DIR"/createColumnPublishMonth.sql"

fi

if [ -f $DATA_DIR"/"$INPUT_DETER_TABLE ]
then

    psql -d "DETER-B" -h 150.163.2.177 -f $DATA_DIR"/drop_"$INPUT_DETER_TABLE
    
    psql -d "DETER-B" -h 150.163.2.177 -f $DATA_DIR"/"$INPUT_DETER_TABLE

    psql -d "DETER-B" -h 150.163.2.177 -f $DATA_DIR"/createColumnPublishMonth.sql"

    echo $DATE": Data was updated." >> $DATA_DIR"/update-deter-amz.log"
else
    echo $DATE": Missing file!!" >> $DATA_DIR"/update-deter-amz.log"
fi