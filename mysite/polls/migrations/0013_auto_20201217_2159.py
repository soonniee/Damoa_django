# Generated by Django 3.1.4 on 2020-12-17 12:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0012_auto_20201217_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='bid_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 17, 21, 59, 16, 92573)),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_start',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 17, 21, 59, 16, 92573)),
        ),
    ]