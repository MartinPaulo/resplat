# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-18 01:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0008_auto_20170818_0034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingest',
            name='extraction_date',
            field=models.DateField(default=datetime.date.today, help_text='the date this data was read'),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='extract_date',
            field=models.DateField(default=datetime.date.today, editable=False, help_text='the date the file was processed', verbose_name='Extract creation date'),
        ),
        migrations.AlterField(
            model_name='request',
            name='institution_faculty',
            field=models.ForeignKey(blank=True, help_text='the UoM Faculty this request belongs to', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_suborganization', to='storage.Suborganization'),
        ),
    ]
