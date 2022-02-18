import os
from publisher_service import PublisherService
from datetime import datetime
import logging

realLogPath = os.path.abspath(os.path.dirname(__file__) + '/../log')

logdatetime = datetime.now().strftime('%d-%m-%Y_%H:%M:%S.%f')
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    # handlers=[
                    #     logging.FileHandler('../log/raster-publisher_' + logdatetime + '.log'),
                    #     logging.StreamHandler()
                    # ],
                    filename= realLogPath + '/raster-publisher_' + logdatetime + '.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

logging.info("Start proccess at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))

execPublisherService = PublisherService()

logging.info("End proccess at {0}".format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')))