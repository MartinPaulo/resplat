# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-16 04:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import storage.models.contacts


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0006_auto_20170816_0415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldofresearch',
            options={'ordering': ['code'], 'verbose_name_plural': 'fields of research'},
        ),
        migrations.AlterModelOptions(
            name='ingestfile',
            options={'ordering': ['extract_date', 'location']},
        ),
        migrations.AlterModelOptions(
            name='label',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='labelsalias',
            options={'verbose_name': 'Label alias', 'verbose_name_plural': 'Label aliases'},
        ),
        migrations.AlterField(
            model_name='allocation',
            name='application',
            field=models.ForeignKey(blank=True, help_text='the original request', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocations', to='storage.Request'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='collection',
            field=models.ForeignKey(help_text='the associated collection', on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocations', to='storage.Project'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='idm_domain',
            field=models.ForeignKey(blank=True, help_text='???', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocation_idm_domain', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='idm_identifier',
            field=models.CharField(blank=True, help_text='???', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='notes',
            field=models.TextField(blank=True, help_text='notes on this allocation', null=True),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='operational_center',
            field=models.ForeignKey(blank=True, help_text='the operational center', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocation_op_center', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='site',
            field=models.ForeignKey(blank=True, help_text='the storage site', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocation_site', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='status',
            field=models.ForeignKey(blank=True, help_text='the status of this allocation', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocation_status', to='storage.Label', verbose_name='allocation status'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='storage_product',
            field=models.ForeignKey(help_text='the storage product to be used for this allocation', on_delete=django.db.models.deletion.DO_NOTHING, related_name='allocations', to='storage.StorageProduct'),
        ),
        migrations.AlterField(
            model_name='collectionprofile',
            name='collection',
            field=models.OneToOneField(help_text='the collection associated with this profile', on_delete=django.db.models.deletion.CASCADE, to='storage.Project'),
        ),
        migrations.AlterField(
            model_name='collectionprofile',
            name='estimated_final_size',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='estimated final size of collection in gigabytes', max_digits=15, null=True, verbose_name='estimated collection final size'),
        ),
        migrations.AlterField(
            model_name='collectionprofile',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='collectionprofile',
            name='merit_justification',
            field=models.TextField(blank=True, help_text='the justification underlying the collection', null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='business_email_address',
            field=models.CharField(blank=True, help_text='the contacts work email address', max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='business_phone_number',
            field=models.CharField(blank=True, help_text='the contacts business phone number', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email_address',
            field=models.CharField(blank=True, help_text='the contacts home email address', max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(help_text='first name of contact', max_length=30, verbose_name='First name of contact'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(help_text='last name of contact', max_length=30, verbose_name='Last name of contact'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='mobile_number',
            field=models.CharField(blank=True, help_text='the contacts mobile number', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='orcid',
            field=models.URLField(blank=True, help_text='the contacts ORCID (if any)', null=True, validators=[storage.models.contacts.validate_orcid], verbose_name='ORCID of contact'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='organisation',
            field=models.ForeignKey(blank=True, help_text='the contacts primary organisation', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='contact_organisation', to='storage.Organisation'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_number',
            field=models.CharField(blank=True, help_text='the contacts home phone number', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='position',
            field=models.ForeignKey(blank=True, help_text='the contacts position at that organisation', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='contact_position', to='storage.Label', verbose_name='Organisation Position'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='title',
            field=models.ForeignKey(blank=True, help_text='the contacts title', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='contact_title', to='storage.Label', verbose_name='Contact Title'),
        ),
        migrations.AlterField(
            model_name='custodian',
            name='collection',
            field=models.ForeignKey(help_text='the collection this custodian is associated with', on_delete=django.db.models.deletion.DO_NOTHING, related_name='custodians', to='storage.Project'),
        ),
        migrations.AlterField(
            model_name='custodian',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='custodian',
            name='person',
            field=models.ForeignKey(help_text='the custodian', on_delete=django.db.models.deletion.DO_NOTHING, to='storage.Contact'),
        ),
        migrations.AlterField(
            model_name='custodian',
            name='role',
            field=models.ForeignKey(help_text='the role of this custodian', on_delete=django.db.models.deletion.DO_NOTHING, related_name='custodian_role', to='storage.Label', verbose_name='Custodian Role'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='collection',
            field=models.ForeignKey(help_text='the associated collection', on_delete=django.db.models.deletion.DO_NOTHING, related_name='domains', to='storage.Project'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='field_of_research',
            field=models.ForeignKey(db_column='fieldofresearch_id', help_text='the field of research', on_delete=django.db.models.deletion.DO_NOTHING, related_name='domains', to='storage.FieldOfResearch', verbose_name='Field of Research'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='domain',
            name='split',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, help_text='percentage split of the total field of research allocation', max_digits=5, null=True, verbose_name='percentage split in decimal'),
        ),
        migrations.AlterField(
            model_name='fieldofresearch',
            name='code',
            field=models.CharField(help_text='the code for the division/group/field', max_length=6, unique=True, verbose_name='the FOR code'),
        ),
        migrations.AlterField(
            model_name='fieldofresearch',
            name='description',
            field=models.CharField(blank=True, help_text='a human readable description of the division/group/field', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='fieldofresearch',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='allocated_capacity',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='the allocated capacity in GB', max_digits=15, null=True, verbose_name='allocated capacity in GB'),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='collection',
            field=models.ForeignKey(help_text='the collection associated with this reading', on_delete=django.db.models.deletion.DO_NOTHING, related_name='ingests', to='storage.Project'),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='extraction_date',
            field=models.DateField(help_text='the date this data was read'),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='storage_product',
            field=models.ForeignKey(help_text='the storage product holding the data', on_delete=django.db.models.deletion.DO_NOTHING, to='storage.StorageProduct'),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='used_capacity',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='the ingested capacity in GB', max_digits=15, null=True, verbose_name='ingested capacity in GB'),
        ),
        migrations.AlterField(
            model_name='ingest',
            name='used_replica',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='??', max_digits=15, null=True, verbose_name='replica ingested capacity in GB'),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='extract_date',
            field=models.DateField(editable=False, help_text='the date the file was processed', verbose_name='Extract creation date'),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='location',
            field=models.SmallIntegerField(choices=[(1, 'Clayton'), (2, 'Queensbury'), (3, 'Noble Park')], db_column='file_location', help_text='the ???'),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='source',
            field=models.CharField(choices=[('MON', 'Monash'), ('UOM', 'University of Melbourne')], db_column='file_source', help_text='the institution the file came from', max_length=3),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='type',
            field=models.CharField(choices=[('M', 'Market'), ('C', 'Computational'), ('V', 'Vault'), ('X', 'Mixed')], db_column='file_type', help_text='the storage product type covered by the file', max_length=1),
        ),
        migrations.AlterField(
            model_name='ingestfile',
            name='url',
            field=models.URLField(db_column='file_name', help_text='where the file was fetched from'),
        ),
        migrations.AlterField(
            model_name='label',
            name='application_flag',
            field=models.BooleanField(default=False, help_text='???'),
        ),
        migrations.AlterField(
            model_name='label',
            name='group',
            field=models.ForeignKey(blank=True, default=1, help_text='the group this label belongs to', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Label_Group', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='label',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='label',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='the parent label, if any', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Label_Parent', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='label',
            name='parent_type',
            field=models.ForeignKey(blank=True, help_text='the type of the parent label, if any', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Label_Parent_Type', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='label',
            name='sequence_number',
            field=models.IntegerField(default=0, help_text='where this label is ordered in the group'),
        ),
        migrations.AlterField(
            model_name='label',
            name='value',
            field=models.CharField(help_text='the value that will be shown to the user', max_length=250),
        ),
        migrations.AlterField(
            model_name='labelsalias',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='labelsalias',
            name='label',
            field=models.ForeignKey(help_text='the label that is aliased', on_delete=django.db.models.deletion.DO_NOTHING, related_name='aliased_label', to='storage.Label', verbose_name='aliased label'),
        ),
        migrations.AlterField(
            model_name='labelsalias',
            name='source',
            field=models.ForeignKey(blank=True, help_text='???', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='alias_source', to='storage.Label', verbose_name='alias source'),
        ),
        migrations.AlterField(
            model_name='labelsalias',
            name='value',
            field=models.CharField(help_text='the value of the alias that will be shown', max_length=100, verbose_name='alias literal value'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='ands_url',
            field=models.URLField(blank=True, help_text='the ANDS url for the organisation', null=True, verbose_name='ANDS url'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.ForeignKey(help_text='the full name for the organisation', on_delete=django.db.models.deletion.DO_NOTHING, related_name='organisation_name', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='rifcs_email',
            field=models.EmailField(blank=True, help_text='the RIFCS contact email address for the organisation', max_length=254, null=True, verbose_name='Notification Email Address'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='short_name',
            field=models.CharField(blank=True, help_text='the brief name for the organisation', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='collective',
            field=models.ForeignKey(blank=True, help_text='???', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='collection_collective', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='project',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.TextField(help_text='the collection name', verbose_name='Collection Name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='overview',
            field=models.TextField(blank=True, help_text='a summary of the collection', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='rifcs_consent',
            field=models.BooleanField(default=False, help_text='is the collection metadata to be made available to the sponsoring institution?', verbose_name='Metadata available to sponsoring institution'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.ForeignKey(blank=True, help_text='the collection status', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='collection_status', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='request',
            name='application_form',
            field=models.URLField(blank=True, help_text='a link to the original request document', null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='capital_funding_source',
            field=models.ForeignKey(blank=True, help_text='where the funding for the collection is being sourced from', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_cap_funding_source', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='request',
            name='code',
            field=models.CharField(help_text='the application code', max_length=15, verbose_name='application code'),
        ),
        migrations.AlterField(
            model_name='request',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='request',
            name='institution',
            field=models.ForeignKey(blank=True, help_text='the institution from which the request comes', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_institution', to='storage.Organisation', verbose_name='sponsoring institution'),
        ),
        migrations.AlterField(
            model_name='request',
            name='institution_faculty',
            field=models.ForeignKey(blank=True, help_text='the UoM Faculty this request belongs to', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_suborganization', to='storage.Suborganization'),
        ),
        migrations.AlterField(
            model_name='request',
            name='node',
            field=models.ForeignKey(blank=True, help_text='VicNode or not?', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Application_Node', to='storage.Label', verbose_name='target node'),
        ),
        migrations.AlterField(
            model_name='request',
            name='notes',
            field=models.TextField(blank=True, help_text='notes about this request', null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='scheme',
            field=models.ForeignKey(blank=True, help_text='the scheme to be used for the collection', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_allocation_scheme', to='storage.Label', verbose_name='allocation scheme'),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.ForeignKey(blank=True, help_text='where the request is in its lifecycle', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_status', to='storage.Label', verbose_name='application status'),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='capacity',
            field=models.DecimalField(decimal_places=2, default=0, help_text='the total capacity of this storage product', max_digits=15),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='operational_center',
            field=models.ForeignKey(blank=True, help_text='this products operational center', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='storage_product_op_center', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='operational_cost',
            field=models.DecimalField(decimal_places=2, default=0, help_text='the operation cost', max_digits=15),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='product_name',
            field=models.ForeignKey(help_text='the name of this storage product', on_delete=django.db.models.deletion.DO_NOTHING, related_name='storageproduct_name', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='raw_conversion_factor',
            field=models.DecimalField(decimal_places=4, default=1, help_text='???', max_digits=6),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='scheme',
            field=models.ForeignKey(help_text='the allocation scheme for this product', on_delete=django.db.models.deletion.DO_NOTHING, related_name='storageproduct_allocation_scheme', to='storage.Label'),
        ),
        migrations.AlterField(
            model_name='storageproduct',
            name='unit_cost',
            field=models.DecimalField(decimal_places=2, default=0, help_text='the cost per unit of storage', max_digits=15),
        ),
        migrations.AlterField(
            model_name='suborganization',
            name='id',
            field=models.AutoField(help_text='the primary key', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='suborganization',
            name='name',
            field=models.TextField(help_text='the full name of a UoM Faculty', verbose_name='faculty'),
        ),
    ]
