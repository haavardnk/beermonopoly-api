# Generated by Django 3.1.12 on 2021-09-22 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beers', '0045_badge'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='type',
            field=models.CharField(default='Top Style', max_length=50),
            preserve_default=False,
        ),
    ]