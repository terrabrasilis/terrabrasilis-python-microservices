#!/usr/bin/python3
from exec_script_service import ExecScriptService

"""
Running daily with cron job to copy data and process intersections.
"""

execScriptService = ExecScriptService()
execScriptService.execScript()