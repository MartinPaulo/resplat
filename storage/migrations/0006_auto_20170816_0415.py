# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-16 04:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('storage', '0005_auto_20170816_0412'),
    ]

    operations = [
        migrations.RenameField('IngestFile', 'file_source', 'source'),
        migrations.RenameField('IngestFile', 'file_location', 'location'),
        migrations.RenameField('IngestFile', 'file_type', 'type'),
        migrations.RenameField('IngestFile', 'file_name', 'url'),
    ]
