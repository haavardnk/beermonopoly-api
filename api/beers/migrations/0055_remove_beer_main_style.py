# Generated by Django 3.2.9 on 2022-01-16 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0054_beer_main_style'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beer',
            name='main_style',
        ),
    ]
