# Generated by Django 3.1.4 on 2020-12-17 11:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0010_auto_20201217_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='bid_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 17, 20, 34, 57, 46546)),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_start',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 17, 20, 34, 57, 46546)),
        ),
    ]