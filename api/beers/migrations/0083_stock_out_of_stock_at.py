# Generated by Django 3.2.16 on 2023-02-06 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0082_auto_20230206_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='out_of_stock_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]