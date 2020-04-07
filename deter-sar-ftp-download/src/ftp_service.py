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
from datetime import date, datetime, timedelta
from common_modules.configuration.src.common_config import ConfigLoader

class FtpService:

    def __init__(self):
        """
        Constructor
        """
        self.docker_env = os.getenv("DOCKER_ENV", False)

        realLogPath = '.'
        # if in production mode
        if self.docker_env:
            realLogPath = '/usr/local/data/log'
        else:
            realLogPath = os.path.abspath(os.path.dirname(__file__) + '/')

        logdatetime = datetime.now().strftime('%d_%m_%Y_%H_%M')
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename= realLogPath + '/deter-sar-download-' + logdatetime + '.log',
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
                absolute_path = '/usr/local/data/config/'

            inputcfg = ConfigLoader(relative_path, 'ftp-credentials.cfg','ftp', absolute_path)
            self.input_cfg = inputcfg.get()
            pathcfg = ConfigLoader(relative_path, 'ftp-paths.cfg', section, absolute_path)
            self.path_cfg = pathcfg.get()

            self.ftp_user = os.getenv("FTP_USER", "/tmp/deter-ftp-download/ftp.dpi.user")
            if self.ftp_user and os.path.isfile(self.ftp_user):
                self.ftp_user = open(self.ftp_user).read()
            else:
                raise Exception('Failure when reading env FTP_USER.')

            self.ftp_pass = os.getenv("FTP_PASS", "/tmp/deter-ftp-download/ftp.dpi.pass")
            if self.ftp_pass and os.path.isfile(self.ftp_pass):
                self.ftp_pass = open(self.ftp_pass).read()
            else:
                raise Exception('Failure when reading env FTP_PASS.')

            # read the destination directory to downloaded files
            self.downloadTo = os.path.realpath(self.path_cfg["download"])
            # read the file name of text configuration used as a trigger
            self.txtFileName = self.path_cfg["txt_file_name"]

        except Exception as error:
            self.__log(repr(error))
            self.__log("Failure when loading initial configurations.")

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
        if(zipFileName):
            self.download(zipFileName)
            self.unzipShape(zipFileName)
            self.setShpName(os.path.splitext(zipFileName)[0])
            if(removeLocalFiles):
                self.removeLocalFile(self.txtFileName)
                self.removeLocalFile(zipFileName)

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
            self.__log("Failure on download process...")

    def __log(self, value):
        """
        Write log
        @param value The message to write into log file.
        """
        time = format(datetime.today().strftime('%d-%m-%Y %H:%M:%S.%f'))   
        logging.debug("{0} - {1}".format(time, value))