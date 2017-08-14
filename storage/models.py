import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


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
    idm_domain = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='IDM Domain'),
        blank=True, null=True, related_name='allocation_idm_domain')
    application = models.ForeignKey(
        'storage.Request', models.DO_NOTHING,
        blank=True, null=True, related_name='allocations')
    collection = models.ForeignKey(
        'storage.Project', models.DO_NOTHING,
        related_name='allocations')
    operational_center = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Operational Center'),
        blank=True, null=True, related_name='allocation_op_center')
    site = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Data Center'),
        blank=True, null=True, related_name='allocation_site')
    status = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Allocation Status'),
        blank=True, null=True, related_name='allocation_status',
        verbose_name='allocation status')
    storage_product = models.ForeignKey(
        'storage.StorageProduct', models.DO_NOTHING,
        related_name='allocations')

    def __str__(self):
        return self.collection.name

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

    def __str__(self):
        return self.collection.name

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
    role = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Custodian Role'),
        verbose_name='Custodian Role', related_name='custodian_role')

    def __str__(self):
        return " ".join(
            [self.collection.name, self.person.full_name, self.role.value])

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
    field_of_research = models.ForeignKey('FieldOfResearch', models.DO_NOTHING,
                                          verbose_name='Field of Research',
                                          related_name='domains',
                                          db_column='fieldofresearch')

    def __str__(self):
        return " ".join(filter(None, [self.collection.name,
                                      self.field_of_research.code,
                                      self.field_of_research.description]))

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

    def __str__(self):
        return " ".join([self.code, self.description])

    class Meta:
        db_table = 'applications_fieldofresearch'
        ordering = ['code']
        verbose_name_plural = "fields of research"


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

    @property
    def ingested_tb(self):
        "The ingested amount in Terabytes"
        return self.used_capacity / 1000

    def __str__(self):
        return " ".join(filter(None,
                               [self.collection.name,
                                self.storage_product.product_name.value]))

    class Meta:
        db_table = 'applications_ingest'
        unique_together = ('extraction_date', 'collection', 'storage_product')
        indexes = [models.Index(
            fields=['collection', 'storage_product', 'extraction_date'])]


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
    collective = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Collective'),
        blank=True, null=True, related_name='collection_collective')
    status = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Collection Status'),
        blank=True, null=True, related_name='collection_status')
    rifcs_consent = models.BooleanField(
        default=False,
        verbose_name='Meta data available to sponsoring institution')

    def __str__(self):
        return self.name

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
        limit_choices_to=Q(group__value__exact='Funding Code'),
        related_name='application_cap_funding_source')
    institution = models.ForeignKey(
        'storage.Organisation', models.DO_NOTHING, blank=True, null=True,
        verbose_name='sponsoring institution',
        related_name='application_institution')
    node = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Node'),
        blank=True, null=True,
        verbose_name='target node', related_name='Application_Node')
    scheme = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Allocation Scheme'),
        verbose_name='allocation scheme',
        related_name='application_allocation_scheme')
    status = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Application Status'),
        verbose_name='application status', related_name='application_status')
    institution_faculty = models.ForeignKey(
        'storage.Suborganization', models.DO_NOTHING, blank=True,
        null=True,
        related_name='application_suborganization')

    def __str__(self):
        return self.code

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
    product_name = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Storage Product'),
        related_name='storageproduct_name')
    scheme = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Allocation Scheme'),
        related_name='storageproduct_allocation_scheme')
    operational_center = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Operational Center'),
        related_name='storage_product_op_center')

    def __str__(self):
        return self.product_name.value

    class Meta:
        db_table = 'applications_storageproduct'


class Suborganization(models.Model):
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

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'applications_suborganization'
        verbose_name = 'Suborganization'


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
    position = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Position'),
        verbose_name='Organisation Position', related_name='contact_position')
    title = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Title'),
        verbose_name='Contact Title', related_name='contact_title')

    @property
    def full_name(self):
        """Returns the person's full name."""
        return " ".join(filter(None, [self.first_name, self.last_name]))

    def __str__(self):
        return self.full_name

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
    name = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Organisation'),
        related_name='organisation_name')
    rifcs_email = models.EmailField(blank=True, null=True,
                                    verbose_name='Notification Email Address')
    ands_url = models.URLField(blank=True, null=True,
                               verbose_name='ANDS Url')

    def __str__(self):
        return self.name.value

    class Meta:
        db_table = 'contacts_organisation'


class IngestFile(models.Model):
    """
    Removed:
        completed
    """
    SOURCE_CHOICES = (('MON', 'Monash'), ('UOM', 'University of Melbourne'))
    SOURCE_LOCATIONS = ((1, 'Clayton'), (2, 'Queensbury'), (3, 'Noble Park'))
    TYPE_CHOICES = (('M', 'Market'), ('C', 'Computational'), ('V', 'Vault'),
                    ('X', 'Mixed'))
    id = models.AutoField(primary_key=True)
    source = models.CharField(
        max_length=3, choices=SOURCE_CHOICES, null=False,
        db_column='file_source')
    location = models.SmallIntegerField(
        null=False, choices=SOURCE_LOCATIONS, db_column='file_location')
    type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, null=False, db_column='file_type')
    extract_date = models.DateField(
        'Extract creation date', editable=False, blank=False, null=False)
    url = models.URLField(db_column='file_name')

    def __str__(self):
        return f'{self.extract_date} {self.source} ' \
               f'{self.get_location_display()} {self.url}'

    class Meta:
        db_table = 'ingest_ingestfile'
        ordering = ['extract_date', 'location']


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
    source = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Alias Source'),
        related_name='alias_source', verbose_name='alias source')

    def __str__(self):
        return self.value

    class Meta:
        db_table = 'labels_alias'
        verbose_name = 'Label alias'
        verbose_name_plural = 'Label aliases'
        unique_together = ('label', 'value')
        indexes = [models.Index(fields=['label'])]


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
                              limit_choices_to=Q(group__value__exact='Label'),
                              related_name='Label_Group',
                              default=1)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True,
                               null=True, related_name='Label_Parent')
    parent_type = models.ForeignKey(
        'self', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Label'),
        related_name='Label_Parent_Type')

    def __str__(self):
        return self.value

    class Meta:
        db_table = 'labels_label'
        unique_together = ('value', 'group')
        indexes = [models.Index(fields=['group', 'value'])]
        ordering = ['id']
