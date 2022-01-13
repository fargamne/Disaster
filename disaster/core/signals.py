import requests
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Event, Trip, Country


def notify_user_calendars(sender, instance, created, **kwargs):
    if created:
        for trip in Trip.objects.filter(
            date_start__lte=instance.date,
            date_end__gte=instance.date,
            location=instance.location
        ):
            requests.post(
                'http://localhost:8080/create_event',
                {
                    'title': instance.title,
                    'date': instance.date.stftime('%Y-%m-%d')
                }
            )


def check_user_calendars(sender, instance, created, **kwargs):
    events = Event.objects.filter(
        date__gte=instance.date_start,
        date__lte=instance.date_end,
        location=instance.location,
    )
    if events.exists():
        for event in events:
            requests.post(
                'http://localhost:8080/create_event',
                {
                    'title': event.title,
                    'date': event.date.stftime('%Y-%m-%d')
                }
            )


def update_statistics(sender, instance, created, **kwargs):
    if created:
        country_qs = Country.objects.filter(title=instance.location)
        if country_qs.exists():
            country = country_qs.first()
            country.heat += 1
            country.save()
        else:
            Country.objects.create(title=instance.location, heat=1)


post_save.connect(update_statistics, sender=Event)
post_save.connect(notify_user_calendars, sender=Event)
post_save.connect(check_user_calendars, sender=Trip)

