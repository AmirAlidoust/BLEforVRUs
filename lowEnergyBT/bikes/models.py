from django.db import models
from .utils import haversine_distance

class Bike(models.Model):
    identifier = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)

    def distance_to(self, lat, lon):
        return haversine_distance(self.latitude, self.longitude, lat, lon)
