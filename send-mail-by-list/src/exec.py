#!/usr/bin/python3
from mail_service import MailService
import os

# to debug, uncomment the following environment vars and guarantee that files exists into your system
# os.environ["MAIL_TO"]="andre.carvalho@inpe.br"
# os.environ["SMTP_GOOGLE_MAIL_USER_FILE"]="/run/secrets/google.mail.user"
# os.environ["SMTP_GOOGLE_MAIL_PASS_FILE"]="/run/secrets/google.mail.pass"
# os.environ["POSTGRES_USER_FILE"]="/run/secrets/postgres.user.geoserver"
# os.environ["POSTGRES_PASS_FILE"]="/run/secrets/postgres.pass.geoserver"

mailService = MailService()
mailService.sendMails()
