import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ))
import logging
from datetime import date, datetime, timedelta
from common_modules.configuration.src.common_config import ConfigLoader

class ProcessService:    

    """
    Constructor
    """
    def __init__(self): 
        self.docker_env = os.getenv("DOCKER_ENV", False)

        realLogPath = os.path.abspath(os.path.dirname(__file__) + '/../log')

        logdatetime = datetime.now().strftime('%d-%m-%Y_%H:%M:%S.%f')
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    # handlers=[
                    #     logging.FileHandler('../log/raster-process_' + logdatetime + '.log'),
                    #     logging.StreamHandler()
                    # ],
                    filename= realLogPath + '/raster-process_' + logdatetime + '.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)
               
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config') + "/"
        self.__loadConfigurations(relative_path)
        self.__translate()

    """
    Configurations loading
    """
    def __loadConfigurations(self, relative_path):
        try:                        
            section = 'developer'
            if self.docker_env:
                section = 'production'

            pathcfg = ConfigLoader(relative_path, 'process-paths.cfg', section)
            self.path_cfg = pathcfg.get()

        except Exception as error:
            self.__log(error)


    """
    Execute GDAL translate
    """
    def __translate(self):
        fromPath = os.path.realpath(self.path_cfg["from"])
        toPath = os.path.realpath(self.path_cfg["to"])
        try:
            filesToTranslate = os.listdir(fromPath)
            for toTranslate in filesToTranslate:
                if ".tif" in toTranslate:  
                    self.__log("Translate file {0}...".format(toTranslate))

                    pathToReadToTranslate = fromPath + "/" + toTranslate
                    pathToMoveAfterTranslate = toPath + "/" + toTranslate

                    # gdal_translate -of GTiff -ot Byte -scale -co TFW=YES
                    cmd = "gdal_translate -of GTiff -ot Byte -scale " + pathToReadToTranslate + " " + pathToMoveAfterTranslate
                    self.__log("Executing cmd: {0}".format(cmd))
                    if os.path.exists(pathToReadToTranslate): 
                        os.system(cmd)
                        if os.path.exists(pathToMoveAfterTranslate):
                            self.__log("Removing file: {0}".format(pathToReadToTranslate))
                            os.remove(pathToReadToTranslate) 

        except Exception as error:
            self.__log(error)
        
    """
    Write log
    """
    def __log(self, value):     
        time = format(datetime.today().strftime('%d-%m-%Y %H:%M:%S.%f'))   
        logging.debug("{0} - {1}".format(time, value))