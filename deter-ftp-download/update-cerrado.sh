#!/bin/sh

DATA_DIR="/usr/local/data"

INPUT_DETER_TABLE="mapeamento_2018.sql"

DATE=$(date +"%Y-%m-%d")

export PGUSER=`cat /run/secrets/postgres.user.deter.cerrado`
export PGPASSWORD=`cat /run/secrets/postgres.pass.deter.cerrado`

if ! [ -f $DATA_DIR"/drop_"$INPUT_DETER_TABLE ]
then

    echo "DROP TABLE public.mapeamento_2018;" > $DATA_DIR"/drop_"$INPUT_DETER_TABLE

fi

if [ -f $DATA_DIR"/"$INPUT_DETER_TABLE ]
then

    psql -d "deter_cerrado_belem" -h "fipcerrado.dpi.inpe.br" -f $DATA_DIR"/drop_"$INPUT_DETER_TABLE
    
    psql -d "deter_cerrado_belem" -h "fipcerrado.dpi.inpe.br" -f $DATA_DIR"/"$INPUT_DETER_TABLE

    echo $DATE": Data was updated." >> $DATA_DIR"/update-deter-cerrado.log"
else
    echo $DATE": Missing file!!" >> $DATA_DIR"/update-deter-cerrado.log"
fi