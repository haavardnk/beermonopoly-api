# Generated by Django 3.1.4 on 2020-12-08 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0002_auto_20201208_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='undappd_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='beer',
            name='vinmonopolet_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
