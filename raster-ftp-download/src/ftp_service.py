"""
 
 1. https://docs.python.org/3.5/library/ftplib.html
 2. https://www.pythonforbeginners.com/code-snippets-source-code/how-to-use-ftp-in-python
 3. https://sourcemaking.com/design_patterns/strategy/python/1
 
 Jether Rodrigues - 22/10/2018

 The responsible of that class is:
    1. Connect to FTP
    2. Try to find the 'geoserver.txt' file and download that 
    3. If has any file to do download, will be executed this action
    4. Remove files
"""

import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ))
import logging
import ftplib, zipfile
from datetime import date, datetime, timedelta
from common_modules.configuration.src.common_config import ConfigLoader

class FtpService:    

    """
    Constructor
    """
    def __init__(self): 
        self.docker_env = os.getenv("DOCKER_ENV", False)
               
        realLogPath = os.path.abspath(os.path.dirname(__file__) + '/../log')

        logdatetime = datetime.now().strftime('%d-%m-%Y_%H:%M:%S.%f')
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    # handlers=[
                    #     logging.FileHandler('../log/raster-ftp-download_' + logdatetime + '.log'),
                    #     logging.StreamHandler()
                    # ],
                    filename= realLogPath + '/raster-ftp-download_' + logdatetime + '.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config') + "/"     
        self.__loadConfigurations(relative_path)
        self.__download()

    """
    Configurations loading
    """
    def __loadConfigurations(self, relative_path):
        try:      
            section = 'developer'
            if self.docker_env:
                section = 'production'

            inputcfg = ConfigLoader(relative_path, 'ftp-credentials.cfg','ftp')
            self.input_cfg = inputcfg.get()
            pathcfg = ConfigLoader(relative_path, 'ftp-paths.cfg', section)
            self.path_cfg = pathcfg.get()

        except Exception as error:
            self.__log(error)

    """
    Connect to FTP server, list files and download then
    """
    def __download(self):
        self.host = self.input_cfg["host"]
        self.user = self.input_cfg["user"]
        self.password = self.input_cfg["password"]
        self.downloadTo = os.path.realpath(self.path_cfg["download_to"])
        self.ftpInputDir = self.path_cfg["download_from"]

        downloadFolder = self.downloadTo
        geoserverFilesToDownload = open("geoserver.txt", "wb")

        ftp = ftplib.FTP(self.host)
        ftp.login(self.user, self.password)
        ftp.set_pasv(True)
        ftp.cwd(self.ftpInputDir)
        ftp.retrbinary('RETR geoserver.txt', geoserverFilesToDownload.write)
        geoserverFilesToDownload.close()        

        geoserverFilesToDownload = open("geoserver.txt", "rb")
        buffer = geoserverFilesToDownload.read()

        toIterate = buffer.split(b";")
        for fileToDownload in toIterate:            
            if fileToDownload != "\r\n":                
                self.__getFile(ftp, (fileToDownload.rstrip(b'\r\n')).decode())

        # for fileToDelete in toIterate:
        #     ftp.delete(fileToDelete)

        ftp.delete('geoserver.txt')
        ftp.quit()
        ftp.close()
        
        self.__log("End download files!")

        filesToUnzip = os.listdir(self.downloadTo)
        for toUnzip in filesToUnzip:
            self.__unZip(toUnzip)

        self.__log("End unzip files!")

    """
    Download file
    """
    def __getFile(self, ftp, filename):
        try:
            self.__log("Download file {0}...".format(filename))

            f = open(self.downloadTo + "/" + filename, 'wb')
            ftp.retrbinary("RETR " + filename, f.write)
            f.close()
        except Exception as error:
            self.__log(error)

    """
    Unzip file
    """
    def __unZip(self, toUnzip):
        try:
            if ".zip" in toUnzip:
                self.__log("Unzip file {0}...".format(toUnzip))

                unzip = zipfile.ZipFile(self.downloadTo + "/" + toUnzip, 'r')
                unzip.extractall(self.downloadTo)
                unzip.close()

                self.__log("Delete file {0}...".format(toUnzip))
                toDelete = self.downloadTo + "/" + toUnzip
                if os.path.exists(toDelete):
                    os.remove(toDelete)

        except Exception as error:
            self.__log(error)
    
    """
    Write log
    """
    def __log(self, value):     
        time = format(datetime.today().strftime('%d-%m-%Y %H:%M:%S.%f'))   
        logging.debug("{0} - {1}".format(time, value))