# Generated by Django 3.1.4 on 2020-12-20 18:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0025_auto_20201220_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='bid_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 21, 3, 1, 51, 5725)),
        ),
        migrations.AlterField(
            model_name='product',
            name='bid_start',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 21, 3, 1, 51, 5725)),
        ),
        migrations.AlterField(
            model_name='product',
            name='now_end',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 21, 3, 1, 51, 5725)),
        ),
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_name', models.CharField(default='', max_length=50)),
                ('seller', models.CharField(max_length=20)),
                ('title', models.CharField(default='', max_length=100)),
                ('content', models.CharField(max_length=150)),
                ('reply', models.IntegerField(default=0)),
                ('reply_content', models.CharField(default='', max_length=150)),
                ('prod_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.product')),
                ('user_id', models.ForeignKey(max_length=20, on_delete=django.db.models.deletion.CASCADE, to='polls.userdamoa')),
            ],
        ),
    ]
