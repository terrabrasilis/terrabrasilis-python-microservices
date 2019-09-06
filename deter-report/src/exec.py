#!/usr/bin/python3
from report_service import ReportService
import os

"""
Running daily with cron job to read data and send email.
"""
reportService = ReportService()
reportService.generateReport()
