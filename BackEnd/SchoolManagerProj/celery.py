# SchoolManagerProj/celery.py

import os
from celery import Celery
import logging,warnings

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

logging.getLogger('absl').setLevel(logging.ERROR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolManagerProj.settings')

app = Celery('SchoolManagerProj')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
