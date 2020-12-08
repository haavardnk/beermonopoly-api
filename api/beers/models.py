from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Beer(models.Model):
    #Vinmonopolet info
    beerid = models.IntegerField(primary_key=True) # ID number on Vinmonopolet
    name = models.CharField(max_length=100)
    brewery = models.CharField(max_length=100)
    abv = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)

    #Untappd info
    uptappdid = models.IntegerField(blank=True, null=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True)
    checkins = models.IntegerField(blank=True, null=True)
    style = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ibu = models.IntegerField(blank=True, null=True)
    picture = models.URLField(blank=True, null=True)

    #Server update times
    vinmonopolet_updated = models.DateTimeField(blank=True, null=True)
    untappd_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.name



