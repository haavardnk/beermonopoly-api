# Generated by Django 3.2.16 on 2023-02-06 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0085_release_release_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='product_selection',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
