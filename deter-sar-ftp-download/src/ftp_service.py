"""
 
 1. https://docs.python.org/3.5/library/ftplib.html
 2. https://www.pythonforbeginners.com/code-snippets-source-code/how-to-use-ftp-in-python
 3. https://sourcemaking.com/design_patterns/strategy/python/1
 
 Andre Carvalho - 03/04/2020

 The responsibility of that class is:
    1. Connect to FTP
    2. Try to find the 'detersar.txt' file and download that
    3. If detersar.txt exists, read the name of ZIP file from that text file
    4. Download the ZIP file from FTP and remove the detersar.txt
    5. Unzip the downloaded ZIP file
    7. Remove downloaded files
"""

import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ))
import logging
import ftplib
import zipfile
from datetime import datetime
from common_modules.configuration.src.common_config import ConfigLoader
from log_table_dao import LogTableDao

class FtpService:

    def __init__(self, logging):
        """
        Constructor
        """
        self.docker_env = os.getenv("DOCKER_ENV", False)
        self.logging=logging

        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config') + "/"

        try:
            self.__loadConfigurations(relative_path)
        except Exception as error:
            self.__log(repr(error))
            raise error

    """
    Configurations loading
    """
    def __loadConfigurations(self, relative_path):
        try:      
            section = 'developer'
            if self.docker_env:
                section = 'production'

            # Default path to config files is /usr/local/data/config/ when runs in production mode
            inputcfg = ConfigLoader(relative_path, 'ftp-credentials.cfg','ftp')
            self.input_cfg = inputcfg.get()
            pathcfg = ConfigLoader(relative_path, 'ftp-paths.cfg', section)
            self.path_cfg = pathcfg.get()

            self.ftp_user = os.getenv("FTP_USER", "/tmp/deter-ftp-download/user.ftp.dpi.inpe.br")
            if self.ftp_user and os.path.isfile(self.ftp_user):
                self.ftp_user = open(self.ftp_user).read()
            else:
                raise Exception('Failure when reading env FTP_USER.')

            self.ftp_pass = os.getenv("FTP_PASS", "/tmp/deter-ftp-download/pass.ftp.dpi.inpe.br")
            if self.ftp_pass and os.path.isfile(self.ftp_pass):
                self.ftp_pass = open(self.ftp_pass).read()
            else:
                raise Exception('Failure when reading env FTP_PASS.')

            # read the destination directory to downloaded files
            self.downloadTo = os.path.realpath(self.path_cfg["download"])
            # read the file name of text configuration used as a trigger
            self.txtFileName = self.path_cfg["txt_file_name"]

        except Exception as error:
            raise error

    def tryLoadFilesFronFtp(self, removeLocalFiles=False):
        """
        1. Connect to FTP
        2. Try to find the 'detersar.txt' file and download that
        3. If detersar.txt exists, read the name of ZIP file from that text file
        4. Download the ZIP file from FTP and remove the detersar.txt
        5. Unzip the downloaded ZIP file
        7. Remove downloaded files
        """
        # download text file
        self.download(self.txtFileName, True)
        zipFileName=self.readFileContent(self.txtFileName)
        if(not zipFileName):
            self.__log("The detersar.txt file is empty.")
        else:
            if(not self.hasBeenImported(zipFileName)):
                self.download(zipFileName)
                self.unzipShape(zipFileName)
                self.setShpName(os.path.splitext(zipFileName)[0])
                if(removeLocalFiles):
                    self.removeLocalFile(self.txtFileName)
                    self.removeLocalFile(zipFileName)
            else:
                self.__log("This file has been imported before. ({0})".format(zipFileName))

    def hasBeenImported(self, fileName):
        """
        Check if file has been imported.
        @return boolean, True if filename is in log data table or False otherwise.
        """
        code=None

        try:
            db = LogTableDao()
            log=db.getLogID(fileName)

            if(log and log["id"]):
                code=True

        except Exception as error:
            self.__log("Failure when read LogID from database.")
            self.__log(repr(error))
        
        return code

    def setShpName(self, shpName):
        myfile = open(self.downloadTo+"/shpname.txt", 'w')
        myfile.write(shpName)
        myfile.close()

    def removeLocalFile(self, fileName):
        if os.path.isfile(self.downloadTo+"/"+fileName):
            os.remove(self.downloadTo+"/"+fileName)

    def unzipShape(self, fileName):
        with zipfile.ZipFile(self.downloadTo+"/"+fileName, 'r') as zip_ref:
            zip_ref.extractall(self.downloadTo+"/")

    def readFileContent(self, fileName):
        content=None
        if os.path.isfile(self.downloadTo+"/"+fileName):
            try:
                fp = open(self.downloadTo+"/"+fileName)
                content=fp.readline()
                content=content.strip()
            finally:
                fp.close()
        return content

    def download(self, fileName, removeOriginFile=False):
        """
        Connect to FTP server and download a file.

        @param: targetDirectory The name of directory to read wanted file.
        @param: fileName The file name to download including an extension. (Ex.: detersar.txt or shapefile.zip)
        
        """
        host = self.input_cfg["host"]
        ftpDirectory = os.path.realpath(self.path_cfg["remote_directory"])

        localFileToDownload = None

        try:
            self.__log("Starting download "+fileName+" file...")

            localFileToDownload = open(self.downloadTo+"/"+fileName, "wb")

            ftp = ftplib.FTP(host)
            ftp.login(self.ftp_user, self.ftp_pass)
            ftp.set_pasv(True)
            ftp.cwd(ftpDirectory+"/")
            ftp.retrbinary('RETR '+fileName, localFileToDownload.write)
            localFileToDownload.close()

            if removeOriginFile:
                ftp.delete(fileName)
            
            ftp.quit()
            ftp.close()

            self.__log("Ended download "+fileName+" file!")

        except Exception as error:
            if localFileToDownload:
                localFileToDownload.close()
            
            if os.path.isfile(self.downloadTo+"/"+fileName):
                os.remove(self.downloadTo+"/"+fileName)
            self.__log(repr(error))
            self.__log("Failure on download file {0}.".format(fileName))

    def __log(self, value):
        """
        Write log
        @param value The message to write into log file.
        """
        time = format(datetime.today().strftime('%d-%m-%Y %H:%M:%S.%f'))   
        self.logging.debug("{0} - {1}".format(time, value))