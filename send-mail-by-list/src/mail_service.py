#!/usr/bin/python3
import os, sys
import traceback
from datetime import datetime
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class MailService:

    def __init__(self):
         # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/mail_service.log'
        else:
            self.LOG_FILE=os.path.realpath(os.path.dirname(__file__)) + '/mail_service.log'

    def sendMails(self):
        # get list mail of user from cfg file
        try:
            mails_path=os.path.realpath(os.path.dirname(__file__)) + '/config/mail_list.cfg'
            with open(mails_path, "r") as mails_file:
                for mailTo in mails_file:
                    self.__setUpMaintenanceMsg(mailTo)
        except BaseException as error:
            self.__writeLog(error)

    def __setUpMaintenanceMsg(self, mailTo):
        """
        Generate the maintenance notice.
        """
        mailSubject='[TerraBrasilis] - Aviso de manutenção programada em 10/08/2020'
        try:
            tpl_path=os.path.realpath(os.path.dirname(__file__)) + '/../templates/tpl_maintenance.html'
            with open(tpl_path, "r") as tpl_file:
                bodyHtml=tpl_file.read()
                self.__sendMail(mailTo, mailSubject, bodyHtml)
        except BaseException as error:
            self.__writeLog(error)

    def __sendMail(self, mailTo, mailSubject, bodyHtml):

        pathToConfigFile = os.path.abspath(os.path.dirname(__file__) + '/config')

        try:
            subject=mailSubject
            mail = SenderMail(pathToConfigFile)
            mail.setEmailTo(mailTo)
            mail.send(subject, '', bodyHtml)
        except BaseException as error:
            self.__writeLog(error)

    def __writeLog(self, error):

        with open(self.LOG_FILE, "a") as lf:
            lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            lf.write(datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
            lf.write('-' * 50)