#!/usr/bin/python3
import os, sys
import traceback
from datetime import date, datetime, timedelta
from exec_script_dao import ExecScriptDao
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class ExecScriptService:

    def __init__(self):
        # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/config/script_service.log'
        else:
            self.LOG_FILE='../data/script_service.log'


    def execScript(self):
        """
        Execute a sql script from one script file. 
        See the configuration for where is the script file in model.cfg file, use the key script_file in publish session.

        No return values.
        
        Will write log if exception occur.
        Will send email after the run is end.
        """

        today_date = datetime.today().strftime('%Y-%m-%d')
        title = "General exec script"

        try:
            dao = ExecScriptDao()
            dao.execDropScript()
            title = dao.execScript()
            detail = "Intersections of the all data from alerts table up to {0}.".format(today_date)
            
            self.__sendMail(detail, title, today_date, True)
            
        except BaseException as error:
            
            logFile = os.path.realpath(os.path.dirname(__file__) + "/" + self.LOG_FILE)
            with open(logFile, "a") as lf:
                lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)
            self.__sendMail('Failure when run sql script. See the log file, {0}, for more detail.'.format(self.LOG_FILE), title, today_date, False)

    def __sendMail(self, msg, title, final_date, state):
        """
        Send email.

        See mail.cfg to change the send email configurations.
        The path to mail.cfg is defined below.
        """
        pathToConfigFile="cerrado-deter/src/config"

        body_msg = ['Information about SQL execution.',
        'State: {0}'.format('Success' if state else 'Failure'),
        '{0}'.format( 'Reference date: {0}'.format(final_date) ),
        'Detailed information:',
        msg
        ]
        body_msg = '\r\n'.join(body_msg)#.encode('utf-8')
        try:
            mail = SenderMail(pathToConfigFile)
            mail.send('[Database-({0})] - information about the last script execution.'.format(title), body_msg)
        except BaseException as error:
            logFile = os.path.realpath(os.path.dirname(__file__) + "/" + self.LOG_FILE)
            with open(logFile, "a") as lf:
                lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
                lf.write(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
                lf.write('-' * 50)