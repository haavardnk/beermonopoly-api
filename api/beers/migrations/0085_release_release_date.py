# Generated by Django 3.2.16 on 2023-02-06 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0084_rename_out_of_stock_at_stock_unstocked_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='release_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
