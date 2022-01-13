from django.conf import settings
from django.db import models
from django.urls import reverse


class Trip(models.Model):
    location = models.CharField(max_length=100)
    date_start = models.DateField()
    date_end = models.DateField()

    def get_absolute_url(self):
        return reverse("trip-detail", kwargs={"id": self.id})

    def __str__(self):
        return f'{self.location} start={self.date_start} end={self.date_end}'


class Event(models.Model):
    title = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f'{self.title} date={self.date}'


class Country(models.Model):
    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ['-heat']
    title = models.CharField(max_length=50, blank=True)
    heat = models.IntegerField()

    def __str__(self):
        return f'{self.title} heat={self.heat}'
