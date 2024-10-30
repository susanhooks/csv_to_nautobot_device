"""Module for nautobot jobs."""
from nautobot.core.celery import register_jobs

jobs = [CSVImportJob]

register_jobs(*jobs)