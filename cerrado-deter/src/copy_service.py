#!/usr/bin/python3
import os
import traceback
from datetime import datetime
from copy_dao import CopyDao
from mail.send import SenderMail

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
        min_view_date = max_view_date = None
        num_alerts = 0

        try:
            dao = CopyDao()
            min_view_date, max_view_date, num_alerts = dao.copy(self.renew)
            detail = "Copy all alerts to the production table for publish table." if self.renew else ""

            if num_alerts == 0:
                detail = "No new alerts to copy to the production table for publish table."
                min_view_date = max_view_date = "no defined"
            else:
                detail = "Processed alerts to the interval between {0} and {1}.".format(min_view_date, max_view_date)
            
            # If there is alerts copied, then send an email
            self.__sendMail(detail, min_view_date, max_view_date, num_alerts, True)
            
        except BaseException as error:
            with open(self.LOG_FILE, "a") as lf:
                lf.write(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)
            # If there is an error, send a failure email
            detail = f"Failure when run copy process. See the log file, {self.LOG_FILE}, for more detail."
            self.__sendMail(msg=detail, min_view_date=min_view_date, max_view_date=max_view_date, num_alerts=num_alerts, state=False)

    def __sendMail(self, msg, min_view_date, max_view_date, num_alerts, state):

        pathToConfigFile="cerrado-deter/src/config"

        max_view_date if max_view_date else 'no defined'
        min_view_date if min_view_date else 'no defined'

        # prepare the body message
        body_msg = ['Daily information about syncronization data.',
        'Last synchronization state: {0}'.format('Success' if state else 'Failure'),
        'Last sync date: {0}'.format(datetime.today().strftime('%d-%m-%Y %H:%M:%S')),
        'Number of alerts copied: {0}'.format(num_alerts),
        f'Alerts copied to date range: {min_view_date} and {max_view_date}',
        'Detailed information:',
        msg
        ]
        body_msg = '\r\n'.join(body_msg)#.encode('utf-8')
        try:
            mail = SenderMail(pathToConfigFile)
            mail.send('[DETER-CERRADO] - {0} on data SYNCHRONIZATION.'.format('Success' if state else 'Failure'), body_msg)
        except BaseException as error:
            with open(self.LOG_FILE, "a") as lf:
                lf.write(''.join(traceback.format_exception(type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)
