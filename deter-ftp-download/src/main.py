import os, sys
from ftp_service import FtpService
from datetime import date, datetime, timedelta
import logging

docker_env = os.getenv("DOCKER_ENV", False)

realLogPath = '.'
# if in production mode
if docker_env:
    realLogPath = '/usr/local/data/log'
else:
    realLogPath = os.path.abspath(os.path.dirname(__file__) + '/../data/log')

logdatetime = datetime.now().strftime('%d_%m_%Y_%H_%M')
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename= realLogPath + '/deter-download-' + logdatetime + '.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

logging.info("Start proccess at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))

# to download deter amazon backup file.
execFtpService = FtpService()
execFtpService.download("amazonia","deter_table.sql")
execFtpService.download("cerrado","mapeamento_2018.sql")

logging.info("End proccess at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))