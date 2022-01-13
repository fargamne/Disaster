from __future__ import absolute_import
import os
# from datetime import datetime, date

# import requests
from celery import Celery
# from celery.schedules import crontab
# from geopy.geocoders import Nominatim

# from core.models import Event

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disaster.settings')

app = Celery("disaster")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#         crontab(hour="*/1"),
#         parse_events(),
#     )



