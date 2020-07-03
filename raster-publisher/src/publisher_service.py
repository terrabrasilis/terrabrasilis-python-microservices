# -*- coding: utf-8 -*-

import os, sys
import shutil
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ))
import logging
import requests

from datetime import date, datetime, timedelta
from common_modules.configuration.src.common_config import ConfigLoader

sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class PublisherService:    

    """
    Constructor
    """
    def __init__(self): 
        self.docker_env = os.getenv("DOCKER_ENV", False)

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
               
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config') + "/"
        self.__loadConfigurations(relative_path)
        self.__manipulateFile()

    """
    Configurations loading
    """
    def __loadConfigurations(self, relative_path):
        try:                        
            section = 'developer'
            if self.docker_env:
                section = 'production'

            pathcfg = ConfigLoader(relative_path, 'publisher-paths.cfg', section)
            self.path_cfg = pathcfg.get()

        except Exception as error:
            self.__log(error)


    """
    Execute file manipulation in file disks
    """
    def __manipulateFile(self):
        fromPath = os.path.realpath(self.path_cfg["from"])
        toPath = os.path.realpath(self.path_cfg["to"])
        
        try:
            sendEmail = False
            filesToMove = os.listdir(fromPath)
            msgToEmailBody = ""
            for toMove in filesToMove:
                if ".tif" in toMove:  
                    fileSplit = toMove.split("_")

                    pathToReadToMove = fromPath + "/" + toMove

                    ## build the complete path
                    month = self.__getStringMonthByNumberMonth(self.__convertNumber(fileSplit[4][2:4]))
                    if month == "Invalid": 
                        pathCompleteToMove = toPath + "/" + fileSplit[0] + "_" + fileSplit[1] + "_" + fileSplit[4][4:]
                    else:
                        pathCompleteToMove = toPath + "/" + fileSplit[0] + "_" + fileSplit[1] + "_" + fileSplit[4][4:] + "/" + month
                    
                    ## if the complete path not exists then create
                    if not os.path.exists(pathCompleteToMove):
                        os.makedirs(pathCompleteToMove)
                    
                    ## move file to publish path
                    self.__log("Move file {0} from {1} to {2}...".format(toMove, pathToReadToMove, pathCompleteToMove))
                    if os.path.exists(pathToReadToMove): 
                        pathCompleteToMove = pathCompleteToMove + "/" + toMove
                        shutil.move(pathToReadToMove, pathCompleteToMove)
                    
                    ## really publish the layers
                    if os.path.exists(pathCompleteToMove): 
                        self.__publish(pathCompleteToMove, toMove)
                        msgToEmailBody = msgToEmailBody + toMove + "\r\n"
                        sendEmail = True
            
            if sendEmail:
                self.__sendMail(msgToEmailBody)
                        
        except Exception as error:
            self.__log(error)

    """
    Execute Geoserver publish layers

    http://docs.python-requests.org/en/latest/user/quickstart/
    """
    def __publish(self, imagePathToPublish, fileToPublish):
        host = self.path_cfg["url"]
        user = self.path_cfg["user"]
        password = self.path_cfg["password"]
        workspace = self.path_cfg["workspace"]

        storage_url = "{0}/rest/workspaces/{1}/coveragestores".format(host,workspace)
        storage_name = fileToPublish.split(".")[0] + "_store"

        remove_storage_url = storage_url + "/" + storage_name + "?recurse=true"

        create_layer_url = storage_url + "/" + storage_name + "/coverages"

        create_storage_url = storage_url + "?configure=all"

        # REST requests ###############################
        headers = {'Content-type' : 'application/xml'}

        # Por segurança, o coverage store é removido para o caso de já existir uma publicação anterior.
        response = requests.delete(remove_storage_url, auth=(user, password))
        self.__log("Geoserver response {0} to delete covarage. Code:  {1}...".format(remove_storage_url, response.text))

        # Cria o coverage store
        response = requests.post(create_storage_url
            , headers=headers
            , data = self.__getStorageXml(workspace, storage_name, imagePathToPublish)
            , auth=(user, password))        
        self.__log("Geoserver response {0} to post covarage. Code:  {1}...".format(create_storage_url, response.text))

        # Publica o layer
        response = requests.post(create_layer_url
        , headers=headers
        , data = self.__getLayerXml(fileToPublish)
        , auth=(user, password))
        self.__log("Geoserver response {0} to post layer. Code:  {1}...".format(create_layer_url, response.text))        
         

    """
    Return the store param
    """
    def __getStorageXml(self, workspace, storeName, fileToPublish):
        
        coverageWorkspace="<workspace>{0}</workspace>".format(workspace)
        coverageUrl="<url>{0}</url>".format(fileToPublish)
        coverageName="<name>{0}</name>".format(storeName)
        coverageDefaults="<enabled>true</enabled><type>GeoTIFF</type>"
        coverageStore="<coverageStore>{0}{1}{2}{3}</coverageStore>".format(coverageName,coverageWorkspace,coverageUrl,coverageDefaults)
        return coverageStore
        # return "<coverageStore><name>" + storeName + "</name><workspace>{0}</workspace><enabled>true</enabled><type>GeoTIFF</type><url>" + fileToPublish + "</url></coverageStore>"
    
    """
    Return the layer param
    """
    def __getLayerXml(self, fileToPublish):
        # Cbers4_AWFI_159_117_18012018_10bits_B13G14R15_contraste.tif
        fileSplit = fileToPublish.split("_")
        
        layerName = fileSplit[0] + "_" + fileSplit[1] + "_" + fileSplit[2] + "_" + fileSplit[3] + "_" + fileSplit[4]
        layerTitle = fileSplit[0] + " " + fileSplit[1] + " " + fileSplit[2] + "_" + fileSplit[3] + " " + fileSplit[4]
        layerAbstract = "Imagem " + fileSplit[0] + " " + fileSplit[1] + " de " + fileSplit[4] + " na orbita-ponto " + fileSplit[2] + "_" + fileSplit[3] + " com contraste. Composicao de bandas " + fileSplit[6]
        
        return "<coverage><name>" + layerName + "</name><title>" + layerTitle + "</title><abstract>" + layerAbstract + "</abstract><dimensions><coverageDimension><name>RED_BAND</name><description>GridSampleDimension[-Infinity,Infinity]</description><range><min>0.0</min><max>255.0</max></range><nullValues><double>0.0</double></nullValues><unit>W.m-2.Sr-1</unit><dimensionType><name>UNSIGNED_8BITS</name></dimensionType></coverageDimension><coverageDimension><name>GREEN_BAND</name><description>GridSampleDimension[-Infinity,Infinity]</description><range><min>0.0</min><max>255.0</max></range><nullValues><double>0.0</double></nullValues><unit>W.m-2.Sr-1</unit><dimensionType><name>UNSIGNED_8BITS</name></dimensionType></coverageDimension><coverageDimension><name>BLUE_BAND</name><description>GridSampleDimension[-Infinity,Infinity]</description><range><min>0.0</min><max>255.0</max></range><nullValues><double>0.0</double></nullValues><unit>W.m-2.Sr-1</unit><dimensionType><name>UNSIGNED_8BITS</name></dimensionType></coverageDimension></dimensions><parameters><entry><string>InputTransparentColor</string><string>#000000</string></entry><entry><string>SUGGESTED_TILE_SIZE</string><string>512,512</string></entry></parameters></coverage>"

    """
    Return a month by number
    """
    def __getStringMonthByNumberMonth(self, numberMonth):
        switcher = {
            1: "janeiro",
            2: "fevereiro",
            3: "marco",
            4: "abril",
            5: "maio",
            6: "junho",
            7: "julho",
            8: "agosto",
            9: "setembro",
            10: "outubro",
            11: "novembro",
            12: "dezembro"
        }
        return switcher.get(numberMonth, "Invalid")

    """
    Convert string to number (int ou float)
    """
    def __convertNumber(self, arg):
        try:
            return int(arg)
        except ValueError:
            return float(arg)

    """
    Send email
    """
    def __sendMail(self, msg):
        """
        Send email.

        See email.cfg to change the send email configurations.
        The path to email.cfg is defined below.
        """
        pathToConfigFile="/usr/local/data/config"

        body_msg = ['Raster image publish information.' + datetime.now().strftime('%d-%m-%Y_%H:%M:%S.%f'), 'Images published: \r\n' +  msg ]
        body_msg = '\r\n'.join(body_msg)#.encode('utf-8')
        try:
            mail = SenderMail(pathToConfigFile)
            mail.send('[GEOSERVER-PUBLISHER] - Publish Raster Images.', body_msg)
        except BaseException as error:
            self.__log(error)

    """
    Write log
    """
    def __log(self, value):     
        time = format(datetime.today().strftime('%d-%m-%Y %H:%M:%S.%f'))   
        logging.info("{0} - {1}".format(time, value))