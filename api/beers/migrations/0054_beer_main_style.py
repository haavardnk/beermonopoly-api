# Generated by Django 3.2.9 on 2022-01-16 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0053_store_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='main_style',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
