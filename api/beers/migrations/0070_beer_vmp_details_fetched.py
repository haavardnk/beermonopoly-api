# Generated by Django 3.2.12 on 2022-03-30 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0069_auto_20220330_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='vmp_details_fetched',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
