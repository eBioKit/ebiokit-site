# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-22 11:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_name', models.CharField(max_length=100, unique=True)),
                ('service', models.CharField(max_length=100)),
                ('version', models.CharField(default=b'0.1', max_length=100)),
                ('title', models.CharField(default=b'New application', max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('categories', models.CharField(max_length=500)),
                ('website', models.CharField(max_length=500)),
                ('port', models.CharField(max_length=100, unique=True)),
                ('type', models.CharField(default=b'1', max_length=1)),
                ('installed', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('date', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='RemoteServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('url', models.CharField(max_length=300)),
                ('enabled', models.BooleanField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('job_id', models.CharField(max_length=100)),
                ('id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('command', models.TextField(default=b'')),
                ('function', models.TextField(default=b'')),
                ('params', models.TextField(default=b'')),
                ('depend', models.TextField(default=b'')),
                ('status', models.CharField(max_length=100)),
            ],
        ),
    ]
