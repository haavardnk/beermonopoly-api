# Generated by Django 3.2.12 on 2022-04-08 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0074_alter_beer_raw_materials'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='allergens',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='beer',
            name='method',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
