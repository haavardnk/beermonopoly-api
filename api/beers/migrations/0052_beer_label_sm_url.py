# Generated by Django 3.2.9 on 2022-01-11 09:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0051_rename_label_url_beer_label_hd_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='label_sm_url',
            field=models.CharField(blank=True, max_length=250, null=True, validators=[django.core.validators.URLValidator()]),
        ),
    ]