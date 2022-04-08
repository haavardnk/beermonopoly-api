from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User


class FCMToken(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True, unique=True)
    token = models.CharField(max_length=250)
