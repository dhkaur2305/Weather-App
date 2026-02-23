from django.db import models

# Create your models here.
class WeatherRecord(models.Model):
    city = models.CharField(max_length = 100)
    country = models.CharField(max_length = 50, blank = True)
    date = models.DateField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length = 100)
    
    def __str__(self):
        return f"{self.city} - {self.date}"