#!/usr/bin/python3
from report_service import ReportService
import os

# to debug, uncomment the following environment vars and guarantee that files exists into your system
os.environ["MAIL_TO"]="andre.carvalho@inpe.br"
os.environ["SMTP_GOOGLE_MAIL_USER_FILE"]="/run/secrets/google.mail.user"
os.environ["SMTP_GOOGLE_MAIL_PASS_FILE"]="/run/secrets/google.mail.pass"
os.environ["POSTGRES_USER_FILE"]="/run/secrets/postgres.user.geoserver"
os.environ["POSTGRES_PASS_FILE"]="/run/secrets/postgres.pass.geoserver"

"""
Running daily with cron job to read data and send email.
"""
reportService = ReportService()
reportService.generateReport()
