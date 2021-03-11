# Generated by Django 3.1.4 on 2020-12-16 12:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_auto_20201216_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='bid_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 16, 21, 57, 9, 967796)),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_start',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 16, 21, 57, 9, 967796)),
        ),
        migrations.AlterField(
            model_name='report',
            name='content',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='report',
            name='title',
            field=models.CharField(default='', max_length=100),
        ),
    ]
