#!/usr/bin/python3
from compute_service import ComputeService
import os

# to debug, uncomment the following environment vars and guarantee that files exists into your system
os.environ["POSTGRES_USER_FILE"]="/run/secrets/postgres.user"
os.environ["POSTGRES_PASS_FILE"]="/run/secrets/postgres.pass"

"""
Running daily with cron job to compute the deforestation speed.
"""
computeService = ComputeService()
computeService.compute()
