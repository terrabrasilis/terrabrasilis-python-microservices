#!/usr/bin/python3
import os, sys
import traceback
from datetime import date, datetime, timedelta
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class EmailService:

    def __init__(self):
        # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/email_service.log'
        else:
            self.LOG_FILE=os.path.realpath(os.path.dirname(__file__)) + '/email_service.log'

    def sendLinkByEmail(self, link, email):
        """
        Prepare the email body and send to user.

        @param link, the link to control the file download.
        @param email, target email of the user.
        """

        bodyHeader='Use o link abaixo para baixar os dados.'
        bodyFooter='Att. Equipe do projeto PRODES.'

        try:
            bodyHtml='<p><a href="'+link+'">'+link+'</a></p>'
            self.__sendMail(bodyHeader, bodyFooter, bodyHtml, email)
        except BaseException as error:
            self.__writeLog(error)

    def __sendMail(self, bodyHeader, bodyFooter, bodyHtml, email):

        pathToConfigFile = os.path.abspath(os.path.dirname(__file__) + '/config')

        bodyHtml = ''.join(bodyHtml)#.encode('utf-8')
        bodyHtml = """\
            <html>
                <head></head>
                <body>
                <p>
                <h3>{0}</h3>
                </p>
                {1}
                <br/>
                <p style="color:#C0C0C0;">{2}</p>
                </body>
            </html>
            """.format(bodyHeader, bodyHtml, bodyFooter)
        try:
            ref_date=datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            subject='[PRODES] - Link para download de dados, solicitação em {0}.'.format(ref_date)
            mail = SenderMail(pathToConfigFile)
            mail.setEmailTo(email)
            mail.send(subject, bodyHeader, bodyHtml)
        except BaseException as error:
            self.__writeLog(error)

    def __writeLog(self, error):

        with open(self.LOG_FILE, "a") as lf:
            lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            lf.write(datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
            lf.write('-' * 50)