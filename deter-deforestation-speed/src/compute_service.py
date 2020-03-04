#!/usr/bin/python3
import os, sys
import traceback
from datetime import date, datetime, timedelta
from data_dao import DataDao

class ComputeService:

    def __init__(self):
         # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/compute_service.log'
        else:
            self.LOG_FILE=os.path.realpath(os.path.dirname(__file__)) + '/compute_service.log'

    def compute(self):

        try:
            dao = DataDao()
        except BaseException as error:
            self.__writeLog(error)

        # prepare the table to receive the computed values
        self.prepareOutputTable(dao)

        # first we identify the deforestation scenarios
        self.detectScenarios(dao)
        # then we compute parameters to all scenarios
        self.computeScenarios(dao)

    def detectScenarios(self, dao):
        """
        Generate the temporary table with clusters of polygons to identify the scenarios of deforestation.
        """
        try:
            dao.makeClusters()
            
        except BaseException as error:
            self.__writeLog(error)

    def prepareOutputTable(self, dao):
        """
        Check if output parameters exists, if not, create its or reset its values.
        """
        try:
            dao.createParameters()
            dao.resetParameters()
        except BaseException as error:
            self.__writeLog(error)

    def computeScenarios(self, dao):
        """
        Compute all parameters for detected scenarios
        """
        try:
            dao.makeClusters()
            clusters=dao.getClusters()
            if(len(clusters)>0):
                for record in clusters:
                    cluster_id=record[0]
                    dao.computeParametersByClusterId(cluster_id)
            
        except BaseException as error:
            self.__writeLog(error)

    def __writeLog(self, error):

        with open(self.LOG_FILE, "a") as lf:
            lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            lf.write(datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
            lf.write('-' * 50)