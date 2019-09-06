#!/usr/bin/python3
import os, sys
import traceback
from datetime import date, datetime, timedelta
from intersection_dao import IntersectionDao
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class IntersectionService:

    def __init__(self):
        # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/intersection_service.log'
        else:
            self.LOG_FILE= os.path.realpath(os.path.dirname(__file__) + '/../') + 'intersection_service.log'

        self.renew = False

    def renewIntersections(self):
        """
        Drop current table and reprocess all data from origin table.
        """
        self.renew = True
        self.execIntersections()

    def execIntersections(self):
        """
        Process the intersections of the alert Features with Municipalities and Unit Conservations.

        No return values.
        
        Will write log if exception occur.
        Will send email after the copy is end.
        """

        final_date = None
        today_date = reference_date = datetime.today().strftime('%Y-%m-%d')

        try:
            dao = IntersectionDao()
            final_date = dao.intersections(self.renew)
            detail = ""

            if final_date:
                detail = "Intersections of the all data from alerts table up to {0}.".format(final_date)
                reference_date = final_date
            else:
                detail = "Intersections of the all data from alerts table up to {0}.".format(today_date)
            
            self.__sendMail(detail, reference_date, True)
            
        except BaseException as error:
            
            with open(self.LOG_FILE, "a") as lf:
                lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)
            self.__sendMail('Failure when run intersection process. See the log file, {0}, for more detail.'.format(self.LOG_FILE), reference_date, False)

    def __sendMail(self, msg, final_date, state):
        """
        Send email.

        See mail.cfg to change the send email configurations.
        The path to mail.cfg is defined below.
        """
        pathToConfigFile="cerrado-deter/src/config"

        body_msg = ['Daily information about intersection data.',
        'Last synchronization state: {0}'.format('Success' if state else 'Failure'),
        '{0}'.format( ( 'More recent date: {0}'.format(final_date) ) if state else ( 'Reference date: {0}'.format(final_date) ) ),
        'Detailed information:',
        msg
        ]
        body_msg = '\r\n'.join(body_msg)#.encode('utf-8')
        try:
            mail = SenderMail(pathToConfigFile)
            mail.send('[DETER-CERRADO] - {0} on data INTERSECTION.'.format('Success' if state else 'Failure'), body_msg)
        except BaseException as error:
            with open(self.LOG_FILE, "a") as lf:
                lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)