# -*- encoding: utf-8 -*-
#!/usr/bin/python3
import textwrap
import smtplib
import sys, os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)+'/../configuration/src'))
from common_config import ConfigLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SenderMail(object):
    def __init__(self, relative_path, filename="email.cfg", section="email"):
        """
        For load configuration to send email use this parameters:
        relative_path = 'the/path/to/config/file/'
        filename = 'email.cfg'
        section = 'session_name_to_email_config'

        """
        cfg = ConfigLoader(relative_path, filename, section)
        cfg_data = cfg.get()
        # get user and password for email account from secrets
        if(cfg_data['servertype'] and cfg_data['servertype']=="google"):
            self.user = os.getenv("SMTP_GOOGLE_MAIL_USER_FILE", "user")
            self.password = os.getenv("SMTP_GOOGLE_MAIL_PASS_FILE", "pass")
        else:
            self.user = os.getenv("SMTP_INPE_MAIL_USER_FILE", cfg_data['mail_user'])
            self.password = os.getenv("SMTP_INPE_MAIL_PASS_FILE", cfg_data['mail_pass'])

        if os.path.exists(self.user):
            self.user = open(self.user, 'r').read()
        if os.path.exists(self.password):
            self.password = open(self.password, 'r').read()
        
        self.email_from = self.user
        
        self.to = os.getenv("MAIL_TO", "to")
        if os.path.exists(self.to):
            self.to = open(self.to, 'r').read()
        # try get alias to email from
        email_alias = os.getenv("MAIL_FROM_ALIAS", "terrabrasilis@dpi.inpe.br")
        if email_alias:
            self.email_from = email_alias

        # connection
        try:
            server = smtplib.SMTP(cfg_data['server'], cfg_data['port'])
            server.ehlo()
            server.starttls()
            server.ehlo
            server.login(self.user, self.password)
            self.server = server
        except Exception as error:
            print('Failure on sent the email.')
            raise Exception('Not connected to SMTP server.')

    def setEmailTo(self, email_to):
        self.to = email_to

    def send(self, subject, bodyText, bodyHtml=None):
        """
        Send a e-mail using the parameters:

        @subject: The title of message
        @bodyText: The body text of the message
        @bodyHtml: The body html of the message
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["To"] = self.to
        bodyText = MIMEText(bodyText.encode('utf-8') ,"plain", "utf-8")
        msg.attach(bodyText)
        if bodyHtml:
            bodyHtml = MIMEText(bodyHtml.encode('utf-8'), "html", "utf-8")
            msg.attach(bodyHtml)

        if self.server:
            self.server.sendmail(
                self.email_from,
                self.to.split(','),
                msg.as_string())
        else:
            print('Not connected to SMTP server.')