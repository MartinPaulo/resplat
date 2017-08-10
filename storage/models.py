import re

from django.core.exceptions import ValidationError
from django.db import models


class Allocation(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
        approval_date
        ingested
    """
    id = models.AutoField(primary_key=True)
    size = models.DecimalField(verbose_name='size of allocation (GB)',
                               max_digits=15, decimal_places=2)
    idm_identifier = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    idm_domain = models.ForeignKey('storage.Label', models.DO_NOTHING,
                                   blank=True,
                                   null=True,
                                   related_name='allocation_idm_domain')
    application = models.ForeignKey('storage.Request', models.DO_NOTHING,
                                    blank=True,
                                    null=True,
                                    related_name='allocations')
    collection = models.ForeignKey('storage.Project', models.DO_NOTHING,
                                   related_name='allocations')
    operational_center = models.ForeignKey('storage.Label', models.DO_NOTHING,
                                           blank=True,
                                           null=True,
                                           related_name='allocation_op_center')
    site = models.ForeignKey('storage.Label', models.DO_NOTHING, blank=True,
                             null=True,
                             related_name='allocation_site')
    status = models.ForeignKey('storage.Label', models.DO_NOTHING, blank=True,
                               null=True,
                               related_name='allocation_status',
                               verbose_name='allocation status')
    storage_product = models.ForeignKey('storage.StorageProduct',
                                        models.DO_NOTHING,
                                        related_name='allocations')

    class Meta:
        db_table = 'applications_allocation'


class CollectionProfile(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
        impact_of_loss
        target_audience
        current_size
        estimated_growth
        migration_assistance_required
        anticipated_growth
        current_storage_medium
        estimated_annual_usage
        growth_estimate_period
        user_access_frequency
        user_interaction blank
    """
    id = models.AutoField(primary_key=True)
    collection = models.OneToOneField('storage.Project')  # unique=True?
    merit_justification = models.TextField(blank=True, null=True)
    estimated_final_size = models.DecimalField(
        help_text='Esimated final size of collection in gigabytes',
        max_digits=15, decimal_places=2,
        verbose_name='estimated collection final size', blank=True, null=True)

    class Meta:
        db_table = 'applications_collectionprofile'


class Custodian(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
    """
    id = models.AutoField(primary_key=True)
    collection = models.ForeignKey('storage.Project', models.DO_NOTHING,
                                   related_name='custodians')
    person = models.ForeignKey('storage.Contact', models.DO_NOTHING)
    role = models.ForeignKey('storage.Label', models.DO_NOTHING,
                             verbose_name='Custodian Role',
                             related_name='custodian_role')

    class Meta:
        db_table = 'applications_custodian'


class Domain(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
    """
    id = models.AutoField(primary_key=True)
    split = models.DecimalField(
        help_text='Percentage split of the total allocation',
        max_digits=5, decimal_places=4, default=0, blank=True, null=True,
        verbose_name='percentage split in decimal')
    collection = models.ForeignKey('storage.Project', models.DO_NOTHING,
                                   related_name='domains')
    fieldofresearch = models.ForeignKey('FieldOfResearch', models.DO_NOTHING,
                                        verbose_name='Field of Research',
                                        related_name='domains')

    class Meta:
        db_table = 'applications_domain'


class FieldOfResearch(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=6, unique=True, verbose_name='for code')
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'applications_fieldofresearch'


class Ingest(models.Model):
    """
    Not quite sure what to ditch/keep yet
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
    """
    id = models.AutoField(primary_key=True)
    extraction_date = models.DateField()
    allocated_capacity = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name='allocated capacity in GB', blank=True, null=True)
    used_capacity = models.DecimalField(max_digits=15, decimal_places=2,
                                        verbose_name='ingested capacity in GB',
                                        blank=True, null=True)
    collection = models.ForeignKey('storage.Project', models.DO_NOTHING,
                                   related_name='ingests')
    storage_product = models.ForeignKey('storage.StorageProduct',
                                        models.DO_NOTHING)
    used_replica = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name='replica ingested capacity in GB', default=0)

    class Meta:
        db_table = 'applications_ingest'


class Project(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
        primary_data_source
    """
    id = models.AutoField(primary_key=True)
    overview = models.TextField(blank=True, null=True)
    name = models.TextField(verbose_name='Collection Name')
    collective = models.ForeignKey('storage.Label', models.DO_NOTHING,
                                   blank=True, null=True,
                                   related_name='collection_collective')
    status = models.ForeignKey('storage.Label', models.DO_NOTHING,
                               blank=True, null=True,
                               related_name='collection_status')
    rifcs_consent = models.BooleanField(
        default=False,
        verbose_name='Meta data available to sponsoring institution')

    class Meta:
        db_table = 'applications_project'


class Request(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
        data_management_solution
        operational_funding_source
        estimated_duration
        requested_start_date
        project # BOGUS!
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=15, verbose_name='application code')
    application_form = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    capital_funding_source = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        related_name='application_cap_funding_source')
    institution = models.ForeignKey(
        'storage.Organisation', models.DO_NOTHING, blank=True, null=True,
        verbose_name='sponsoring institution',
        related_name='application_institution')
    node = models.ForeignKey('storage.Label', models.DO_NOTHING,
                             blank=True, null=True,
                             verbose_name='target node',
                             related_name='Application_Node')
    scheme = models.ForeignKey('storage.Label', models.DO_NOTHING,
                               blank=True, null=True,
                               verbose_name='allocation scheme',
                               related_name='application_allocation_scheme')
    status = models.ForeignKey('storage.Label', models.DO_NOTHING,
                               blank=True, null=True,
                               verbose_name='application status',
                               related_name='application_status')
    institution_faculty = models.ForeignKey(
        'storage.SubOrganization', models.DO_NOTHING, blank=True, null=True,
        related_name='application_suborganization')

    class Meta:
        db_table = 'applications_request'


class StorageProduct(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
    """
    id = models.AutoField(primary_key=True)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    operational_cost = models.DecimalField(max_digits=15, decimal_places=2,
                                           default=0)
    capacity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    raw_conversion_factor = models.DecimalField(max_digits=6, decimal_places=4,
                                                default=1)
    product_name = models.ForeignKey('storage.Label', models.DO_NOTHING,
                                     related_name='storageproduct_name')
    scheme = models.ForeignKey('storage.Label', models.DO_NOTHING,
                               related_name='storageproduct_allocation_scheme')
    operational_center = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        related_name='storage_product_op_center')

    class Meta:
        db_table = 'applications_storageproduct'


class SubOrganization(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField(verbose_name='faculty')

    class Meta:
        db_table = 'applications_suborganization'


def validate_orcid(value):
    pattern = re.compile("http://orcid.org/\w{4}-\w{4}-\w{4}-\w{4}")
    if pattern.match(value):
        return
    raise ValidationError(
        'Required format: http://orcid.org/XXXX-XXXX-XXXX-XXXX, '
        'where X is [0-9,a-z,A-Z]')


class Contact(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        updated_by_id
        last_modified
        active_flag
        show_personal_contact_details
        show_mobile_number
        show_business_contact_details
        notes
    """
    id = models.AutoField(primary_key=True)
    first_name = models.CharField('First name of contact', max_length=30)
    last_name = models.CharField('Last name of contact', max_length=30)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    mobile_number = models.CharField(max_length=30, blank=True, null=True)
    email_address = models.CharField(max_length=75, blank=True, null=True)
    business_phone_number = models.CharField(max_length=30, blank=True,
                                             null=True)
    business_email_address = models.CharField(max_length=75, blank=True,
                                              null=True)
    orcid = models.URLField(blank=True, null=True,
                            verbose_name='ORCID of contact',
                            validators=[validate_orcid])
    organisation = models.ForeignKey('storage.Organisation', models.DO_NOTHING,
                                     blank=True, null=True,
                                     related_name='contact_organisation')
    position = models.ForeignKey('storage.Label', models.DO_NOTHING,
                                 blank=True, null=True,
                                 verbose_name='Organisation Position',
                                 related_name='contact_position')
    title = models.ForeignKey('storage.Label', models.DO_NOTHING,
                              blank=True, null=True,
                              verbose_name='Contact Title',
                              related_name='contact_title')

    class Meta:
        db_table = 'contacts_contact'


class Organisation(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        last_modified
        updated_by_id
        active_flag
        number_weekly_working_days
        number_weekly_working_hours
        operational_center
        operational_staff_petabyte
        operational_staff_role
        salary_overhead
        weeks_of_annual_holiday
        weeks_of_public_holiday
        weeks_of_sick_leave
        year_end
        year_start
    """
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=20, blank=True, null=True)
    name = models.ForeignKey('storage.Label', models.DO_NOTHING,
                             related_name='organisation_name')
    rifcs_email = models.TextField(blank=True, null=True,
                                   verbose_name='Notification Email Address')
    ands_url = models.URLField(blank=True, null=True,
                               verbose_name='ANDS Url')

    class Meta:
        db_table = 'contacts_organisation'


class IngestFile(models.Model):
    """
    Removed:
        completed
    """
    FILE_SOURCE_CHOICES = (
        ('MON', 'Monash'), ('UOM', 'University of Melbourne'))
    FILE_SOURCE_LOCATION = (
        (1, 'Clayton'), (2, 'Queensbury'), (3, 'Noble Park'))
    FILE_TYPE_CHOICES = (
        ('M', 'Market'), ('C', 'Computational'), ('V', 'Vault'),
        ('X', 'Mixed'))
    id = models.AutoField(primary_key=True)
    file_source = models.CharField(max_length=3, choices=FILE_SOURCE_CHOICES,
                                   null=False)
    file_location = models.SmallIntegerField(null=False,
                                             choices=FILE_SOURCE_LOCATION)
    file_type = models.CharField(max_length=1, choices=FILE_TYPE_CHOICES,
                                 null=False)
    extract_date = models.DateField('Extract creation date',
                                    editable=False, blank=False, null=False)
    file_name = models.URLField()

    class Meta:
        db_table = 'ingest_ingestfile'


class LabelsAlias(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        last_modified
        updated_by_id
        active_flag
    """
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=100,
                             verbose_name='alias literal value')
    label = models.ForeignKey('storage.Label', models.DO_NOTHING,
                              related_name='aliased_label',
                              verbose_name='aliased label')
    source = models.ForeignKey('storage.Label', models.DO_NOTHING,
                               blank=True, null=True,
                               related_name='alias_source',
                               verbose_name='alias source')

    class Meta:
        db_table = 'labels_alias'


class Label(models.Model):
    """
    Removed:
        creation_date
        created_by_id
        last_modified
        updated_by_id
        active_flag
    """
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=250)
    sequence_number = models.IntegerField(default=0)
    application_flag = models.BooleanField(default=False)
    group = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True,
                              related_name='Label_Group',
                              default=1)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True,
                               null=True, related_name='Label_Parent')
    parent_type = models.ForeignKey('self', models.DO_NOTHING, blank=True,
                                    null=True,
                                    related_name='Label_Parent_Type')

    class Meta:
        db_table = 'labels_label'
