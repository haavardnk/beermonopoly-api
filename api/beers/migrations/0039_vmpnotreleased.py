# Generated by Django 3.1.12 on 2021-08-25 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0038_auto_20210812_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='VmpNotReleased',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
    ]