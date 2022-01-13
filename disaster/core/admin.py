from django.contrib import admin
from core.models import Trip, Event, Country


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass




