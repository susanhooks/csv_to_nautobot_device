"""Module for nautobot jobs."""
from nautobot.core.celery import register_jobs
from .csv_locations import CSVImportJob

jobs = [CSVImportJob]

register_jobs(*jobs)