# Generated by Django 3.2.9 on 2022-01-11 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0050_matchmanually'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beer',
            old_name='label_url',
            new_name='label_hd_url',
        ),
    ]