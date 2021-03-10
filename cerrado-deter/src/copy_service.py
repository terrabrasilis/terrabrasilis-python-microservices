#!/usr/bin/python3
import os, sys
import traceback
from datetime import date, datetime, timedelta
from copy_dao import CopyDao
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class CopyService:

    def __init__(self):
         # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/sync_service.log'
        else:
            self.LOG_FILE=os.path.realpath(os.path.dirname(__file__) + '/../') + 'sync_service.log'
        self.renew = False

    def renewData(self):
        """
        Drop current table and copy all data from production table.
        """
        self.renew = True
        self.copyData()

    def copyData(self):
        """
        Process the copy features from production database to publish database.
        """
        # the start_date is the maximum created_date collected before the synchronization
        start_date = max_created_date = max_view_date = "no defined"

        try:
            dao = CopyDao()
            start_date, max_created_date, max_view_date = dao.copy(self.renew)
            detail = ""

            if self.renew:
                detail = "Copy all alerts to the production table for publish table."
            else:
                detail = "Processed alerts to the interval between {0} and {1}.".format(start_date, max_created_date)
            self.__sendMail(detail, max_created_date, True)
            
        except BaseException as error:
            with open(self.LOG_FILE, "a") as lf:
                lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)
            self.__sendMail('Failure when run copy process. See the log file, {0}, for more detail.'.format(self.LOG_FILE), max_created_date, max_view_date, False)

    def __sendMail(self, msg, max_created_date, max_view_date, state):

        pathToConfigFile="cerrado-deter/src/config"

        body_msg = ['Daily information about syncronization data.',
        'Last synchronization state: {0}'.format('Success' if state else 'Failure'),
        'Last sync date: {0}'.format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')),
        'More recent max_created_date: {0}'.format( max_created_date if max_created_date else 'no defined' ),
        'More recent max_view_date: {0}'.format( max_view_date if max_view_date else 'no defined' ),
        'Detailed information:',
        msg
        ]
        body_msg = '\r\n'.join(body_msg)#.encode('utf-8')
        try:
            mail = SenderMail(pathToConfigFile)
            mail.send('[DETER-CERRADO] - {0} on data SYNCHRONIZATION.'.format('Success' if state else 'Failure'), body_msg)
        except BaseException as error:
            with open(self.LOG_FILE, "a") as lf:
                lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)
