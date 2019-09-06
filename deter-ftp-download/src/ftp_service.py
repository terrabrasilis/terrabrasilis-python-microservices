"""
 
 1. https://docs.python.org/3.5/library/ftplib.html
 2. https://www.pythonforbeginners.com/code-snippets-source-code/how-to-use-ftp-in-python
 3. https://sourcemaking.com/design_patterns/strategy/python/1
 
 Andre Carvalho - 21/03/2019

 The responsibility of that class is:
    1. Connect to FTP
    2. Try to find the 'deter_table.sql.bkp' file and download that 
    4. Remove the 'deter_table.sql.bkp' file
"""

import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ))
import logging
import ftplib
from datetime import date, datetime, timedelta
from common_modules.configuration.src.common_config import ConfigLoader

class FtpService:


    def __init__(self):
        """
        Constructor
        
        @param: targetDirectory The name of directory to read BKP file. Can have amazonia or cerrado.
        @param: bkpFileName The BKP file name.
        
        """
        self.docker_env = os.getenv("DOCKER_ENV", False)

        realLogPath = '.'
        # if in production mode
        if self.docker_env:
            realLogPath = '/usr/local/data/log'
        else:
            realLogPath = os.path.abspath(os.path.dirname(__file__) + '/../data/log')

        logdatetime = datetime.now().strftime('%d_%m_%Y_%H_%M')
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename= realLogPath + '/deter-download-' + logdatetime + '.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config') + "/"     
        self.__loadConfigurations(relative_path)

    """
    Configurations loading
    """
    def __loadConfigurations(self, relative_path):
        try:      
            section = 'developer'
            absolute_path = ''
            if self.docker_env:
                section = 'production'
                absolute_path = '/usr/local/deter-ftp-download/src/config/'

            inputcfg = ConfigLoader(relative_path, 'ftp-credentials.cfg','ftp', absolute_path)
            self.input_cfg = inputcfg.get()
            pathcfg = ConfigLoader(relative_path, 'ftp-paths.cfg', section, absolute_path)
            self.path_cfg = pathcfg.get()

            self.ftp_user = os.getenv("FTP_USER", False)
            if self.ftp_user and os.path.isfile(self.ftp_user):
                self.ftp_user = open(self.ftp_user).read()
            else:
                raise Exception('Failure when reading env FTP_USER.')

            self.ftp_pass = os.getenv("FTP_PASS", False)
            if self.ftp_pass and os.path.isfile(self.ftp_pass):
                self.ftp_pass = open(self.ftp_pass).read()
            else:
                raise Exception('Failure when reading env FTP_PASS.')

        except Exception as error:
            self.__log(repr(error))
            self.__log("Failure when loading initial configurations.")

    def download(self, targetDirectory, fileName, removeOriginFile=False):
        """
        Connect to FTP server and download bkp file.

        @param: targetDirectory The name of directory to read BKP file. Can have amazonia or cerrado.
        @param: fileName The backup file name without ".bkp" extension.
        
        """
        self.host = self.input_cfg["host"]
        self.downloadTo = os.path.realpath(self.path_cfg["download"])
        self.ftpDirectory = os.path.realpath(self.path_cfg["remote_directory"])

        bkpFileName = fileName+".bkp"
        localFileToDownload = None

        try:
            self.__log("Starting download "+fileName+" file...")

            localFileToDownload = open(self.downloadTo+"/"+bkpFileName, "wb")

            ftp = ftplib.FTP(self.host)
            ftp.login(self.ftp_user, self.ftp_pass)
            ftp.set_pasv(True)
            ftp.cwd(self.ftpDirectory+"/"+targetDirectory)
            ftp.retrbinary('RETR '+bkpFileName, localFileToDownload.write)
            localFileToDownload.close()

            if removeOriginFile:
                ftp.delete(bkpFileName)
            
            ftp.quit()
            ftp.close()
            if os.path.isfile(self.downloadTo+"/"+bkpFileName):
                # check if downloaded file size is major than 1MB before proceed.
                if os.path.getsize(self.downloadTo+"/"+bkpFileName)>1000000:
                    if os.path.isfile(self.downloadTo+"/"+fileName):
                        os.remove(self.downloadTo+"/"+fileName)
                    os.rename(self.downloadTo+"/"+bkpFileName, self.downloadTo+"/"+fileName)
                else: # If not, abort.
                    os.remove(self.downloadTo+"/"+bkpFileName)
                    self.__log("The downloaded file is minor than 1MB so will be removed.")
            
            self.__log("Ended download "+fileName+" file!")

        except Exception as error:
            if localFileToDownload:
                localFileToDownload.close()
            
            if os.path.isfile(self.downloadTo+"/"+bkpFileName):
                os.remove(self.downloadTo+"/"+bkpFileName)
            self.__log(repr(error))
            self.__log("Failure on download process...")

    def __log(self, value):
        """
        Write log
        @param value The message to write into log file.
        """
        time = format(datetime.today().strftime('%d-%m-%Y %H:%M:%S.%f'))   
        logging.debug("{0} - {1}".format(time, value))