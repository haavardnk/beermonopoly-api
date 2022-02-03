# Generated by Django 3.2.11 on 2022-02-03 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0059_wishlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('beer', models.ManyToManyField(to='beers.Beer')),
            ],
        ),
    ]
