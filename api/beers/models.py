from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator

class Beer(models.Model):
    #Vinmonopolet info
    vmp_id = models.BigIntegerField(primary_key=True) # ID number on Vinmonopolet
    vmp_name = models.CharField(max_length=100)
    main_category = models.CharField(max_length=50, blank=True, null=True)
    sub_category = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    product_selection = models.CharField(max_length=50, blank=True, null=True)
    vmp_url = models.CharField(max_length=150, validators=[URLValidator()], blank=True, null=True)

    #Untappd info
    untpd_id = models.IntegerField(blank=True, null=True)
    untpd_name = models.CharField(max_length=100, blank=True, null=True)
    untpd_url = models.CharField(max_length=150, validators=[URLValidator()], blank=True, null=True)
    verified_match = models.BooleanField(default=False)
    match_manually = models.BooleanField(default=False)
    prioritize_recheck = models.BooleanField(default=False)
    brewery = models.CharField(max_length=100, blank=True, null=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True)
    checkins = models.IntegerField(blank=True, null=True)
    style = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    abv = models.FloatField(blank=True, null=True)
    ibu = models.IntegerField(blank=True, null=True)
    label_url = models.CharField(max_length=150, validators=[URLValidator()], blank=True, null=True)

    #Server update times
    vmp_updated = models.DateTimeField(blank=True, null=True)
    untpd_updated = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.vmp_name

class Store(models.Model):
    store_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipcode = models.IntegerField()
    category = models.CharField(max_length=50)
    gps_lat = models.FloatField()
    gps_long = models.FloatField()

    store_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    stock_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['store', 'beer']]

    def __str__(self):
        return self.beer.vmp_name


class ExternalAPI(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    baseurl = models.TextField(validators=[URLValidator()], blank=True, null=True)
    api_client_id = models.CharField(max_length=100, blank=True, null=True)
    api_client_secret = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class MatchFilter(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

