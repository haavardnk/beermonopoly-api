# Generated by Django 3.2.12 on 2022-04-05 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0072_auto_20220330_2024'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beer',
            old_name='vintage',
            new_name='year',
        ),
    ]
