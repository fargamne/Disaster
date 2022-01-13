from datetime import datetime

import requests
from celery.schedules import crontab
from geopy import Nominatim

from core.models import Event
from disaster.celery import app


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour="*/1"),
        parse_events(),
    )


@app.task
def parse_events():
    geolocator = Nominatim(user_agent="geoapiExercises")

    events_resp = requests.get('https://eonet.gsfc.nasa.gov/api/v3/events')

    events_list = events_resp.json()['events']

    for event in events_list:
        latitude = event['geometry'][0]['coordinates'][1]
        longitude = event['geometry'][0]['coordinates'][0]
        date_string = event['geometry'][0]['date'].split('T')[0]
        title = event['title']
        event_date = datetime.strptime(date_string, '%Y-%m-%d')
        location = geolocator.reverse(f"{latitude},{longitude}", language='en')
        if location and 'country' in location.raw['address']:
            address = location.raw['address']
            Event.objects.update_or_create(
                defaults={'title': title},
                date=event_date,
                location=address['country']
            )
