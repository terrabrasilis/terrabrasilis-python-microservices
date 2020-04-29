import os, sys
from ftp_service import FtpService
from datetime import datetime
import logging

docker_env = os.getenv("DOCKER_ENV", False)

realLogPath = '.'
# if in production mode
if docker_env:
    realLogPath = '/usr/local/data/log'
else:
    realLogPath = os.path.abspath(os.path.dirname(__file__) + '/')

logdatetime = datetime.now().strftime('%d_%m_%Y')
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename= realLogPath + '/deter-sar-download-' + logdatetime + '.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filemode='a+',
                    level=logging.DEBUG)

logging.info("Starting process at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))

try:
    # to download deter SAR amazon shapefile.
    ftpService = FtpService(logging)
    ftpService.tryLoadFilesFronFtp(True)
except Exception as error:
    logging.critical("Abnormal end of process at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))
    os._exit(999)

logging.info("Ended process at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))