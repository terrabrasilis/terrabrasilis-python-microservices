## Cron job DETER - SAR

This service is a scheduled task to download SAR data from FTP and import it into a database.

The strategy adopted here is to search for a file called detersar.txt every ten minutes in a specific location on an FTP. If such a file exists, it will be downloaded and its contents read. We expect a name of the compressed shapefile in ZIP format and, if that file exists, we download, unzip and import it into a database table.

The text file is a trigger and point to the desired file.

After process the download of shapefile.zip, the text file is deleted.