# Generated by Django 3.1.4 on 2020-12-17 08:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0009_auto_20201216_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='prod_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 17, 17, 39, 5, 686214)),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_start',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 17, 17, 39, 5, 686214)),
        ),
    ]
