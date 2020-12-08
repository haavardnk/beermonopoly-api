from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator

class Beer(models.Model):
    #Vinmonopolet info
    beerid = models.BigIntegerField(primary_key=True) # ID number on Vinmonopolet
    name = models.CharField(max_length=100)
    brewery = models.CharField(max_length=100)
    abv = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    vinmonopolet_url = models.TextField(validators=[URLValidator()], blank=True, null=True)

    #Untappd info
    untappd_id = models.IntegerField(blank=True, null=True)
    verified_match = models.BooleanField(default=False)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True)
    checkins = models.IntegerField(blank=True, null=True)
    style = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ibu = models.IntegerField(blank=True, null=True)
    label_url = models.TextField(validators=[URLValidator()], blank=True, null=True)
    undappd_url = models.TextField(validators=[URLValidator()], blank=True, null=True)

    #Server update times
    vinmonopolet_updated = models.DateTimeField(blank=True, null=True)
    untappd_updated = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.name

class SiteSetting(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    url = models.TextField(validators=[URLValidator()], blank=True, null=True)
    api_client_id = models.CharField(max_length=100, blank=True, null=True)
    api_client_secret = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


