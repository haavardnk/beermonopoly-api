# Generated by Django 3.1.12 on 2021-08-12 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0037_wrongmatch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beer',
            name='untpd_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='beer',
            name='vmp_name',
            field=models.CharField(max_length=150),
        ),
    ]
