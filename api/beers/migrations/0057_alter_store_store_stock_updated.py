# Generated by Django 3.2.9 on 2022-01-16 20:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0056_store_store_stock_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='store_stock_updated',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
