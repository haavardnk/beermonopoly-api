# Generated by Django 3.2.12 on 2022-02-17 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0065_auto_20220217_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beer',
            name='allergens',
        ),
        migrations.RemoveField(
            model_name='beer',
            name='aroma',
        ),
        migrations.RemoveField(
            model_name='beer',
            name='color',
        ),
        migrations.RemoveField(
            model_name='beer',
            name='taste',
        ),
    ]