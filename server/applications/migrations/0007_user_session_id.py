# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-07 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0006_auto_20171128_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='session_id',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
