## Cron job DETER - CRA to SJC

Service to download the backup files of terrabrasilis.deter_table from FTP, drop the old table and import into local database.
For eventual use when the DETER server in Belém is off-line.

## Develop

To create the virtual env for local debug:

```sh
virtualenv --python=/usr/bin/python3 env

# to activate
source env/bin/activate

# to deactivate
deactivate
```