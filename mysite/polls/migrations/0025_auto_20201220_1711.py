# Generated by Django 3.1.4 on 2020-12-20 08:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0024_auto_20201220_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='now_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 20, 17, 11, 31, 653249)),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_start',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 20, 17, 11, 31, 653249)),
        ),
        migrations.AlterField(
            model_name='product',
            name='now_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 20, 17, 11, 31, 653249)),
        ),
    ]
