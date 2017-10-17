import datetime

from django.db import models
from django.db.models import Q, Sum

from storage.models.labels import GroupDefaultLabel


class AccessLayer(models.Model):
    """
    The manner in which the data is to be accessed.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    description = models.CharField(
        max_length=200, blank=False, null=False,
        help_text='the manner in which the data is to be accessed')
    source = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Access Layer Source'),
        default=GroupDefaultLabel('Access Layer Source'),
        related_name='access_layer',
        help_text='the access layer source')

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'applications_accesslayer'


class AccessLayerMember(models.Model):
    """
    Maps access layers to collections

    A new table

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    collection = models.ForeignKey(
        'storage.Collection', related_name='collections',
        help_text='the collection this access layer is associated with',
        default=1)
    accesslayer = models.ForeignKey(
        'storage.AccessLayer', models.DO_NOTHING, related_name='accesslayer',
        help_text='the access layer this collection is associated with',
        default=1)

    def __str__(self):
        return " ".join(
            [self.collection.name, self.accesslayer.description])

    class Meta:
        db_table = 'access_layer_member'


class Allocation(models.Model):
    """
    An allocation associated with the collection

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag
    * approval_date
    * ingested

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    size = models.DecimalField(verbose_name='size of allocation (GB)',
                               max_digits=15, decimal_places=2)
    notes = models.TextField(
        blank=True, null=True,
        help_text='notes on this allocation')
    idm_domain = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='IDM Domain'),
        default=GroupDefaultLabel('IDM Domain'),
        related_name='allocation_idm_domain',
        help_text='the identity management domain (idm)')
    idm_identifier = models.CharField(
        max_length=50, blank=True, null=True,
        help_text='the identifier within the idm domain')
    application = models.ForeignKey(
        'storage.Request', models.DO_NOTHING,
        blank=True, null=True, related_name='allocations',
        help_text='the original request')
    collection = models.ForeignKey(
        'storage.Collection', models.DO_NOTHING,
        related_name='allocations',
        help_text='the associated collection')
    operational_center = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Operational Center'),
        default=GroupDefaultLabel('Operational Center'),
        related_name='allocation_op_center',
        help_text='the operational center')
    site = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Data Center'),
        default=GroupDefaultLabel('Data Center'),
        related_name='allocation_site',
        help_text='the storage site')
    status = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Allocation Status'),
        default=GroupDefaultLabel('Allocation Status'),
        related_name='allocation_status', verbose_name='allocation status',
        help_text='the status of this allocation')
    storage_product = models.ForeignKey(
        'storage.StorageProduct', models.DO_NOTHING,
        related_name='allocations',
        help_text='the storage product to be used for this allocation')

    @property
    def size_tb(self):
        """Returns the size of the allocation in Terabytes"""
        return self.size / 1000

    @property
    def capital_cost(self):
        """Returns the capital cost of the allocation"""
        return self.size_tb * self.storage_product.unit_cost

    @property
    def operational_cost(self):
        """Returns the operational cost of the allocation"""
        return self.size_tb * self.storage_product.operational_cost

    def __str__(self):
        return self.collection.name

    class Meta:
        db_table = 'applications_allocation'


class CollectionProfile(models.Model):
    """
    A brief outline of the collection.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag
    * impact_of_loss
    * target_audience
    * current_size
    * estimated_growth
    * migration_assistance_required
    * anticipated_growth
    * current_storage_medium
    * estimated_annual_usage
    * growth_estimate_period
    * user_access_frequency
    * user_interaction blank


    """
    # Todo: restore the impact_of_loss, migration_assistance_required and
    # the anticipated_growth fields
    id = models.AutoField(primary_key=True, help_text='the primary key')
    collection = models.OneToOneField(
        'storage.Collection',
        help_text='the collection associated with this profile')
    #  Todo: rename merit_justification to 'description'
    merit_justification = models.TextField(
        blank=True, null=True,
        help_text='description of what the collection is')
    estimated_final_size = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name='estimated collection final size',
        help_text='estimated final size of collection in gigabytes')

    def __str__(self):
        return self.collection.name

    class Meta:
        db_table = 'applications_collectionprofile'


class Custodian(models.Model):
    """
    The custodians of the collection, and their roles.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    collection = models.ForeignKey(
        'storage.Collection', related_name='custodians',
        help_text='the collection this custodian is associated with')
    person = models.ForeignKey(
        'storage.Contact', models.DO_NOTHING, help_text='the custodian')
    role = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Custodian Role'),
        verbose_name='Custodian Role', related_name='custodian_role',
        default=GroupDefaultLabel('Custodian Role'),
        help_text='the role of this custodian')

    def __str__(self):
        return " ".join(
            [self.collection.name, self.person.full_name, self.role.value])

    class Meta:
        db_table = 'applications_custodian'


class Domain(models.Model):
    """
    The spread of field of research classification codes for the collection.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    collection = models.ForeignKey(
        'storage.Collection', related_name='domains',
        help_text='the associated collection')
    field_of_research = models.ForeignKey(
        'FieldOfResearch', models.DO_NOTHING,
        verbose_name='Field of Research', related_name='domains',
        db_column='fieldofresearch_id',
        help_text='the field of research')
    split = models.DecimalField(
        max_digits=5, decimal_places=4, blank=True, null=True, default=0,
        verbose_name='percentage split in decimal',
        help_text='percentage split of the total field of research allocation')

    def __str__(self):
        return " ".join(filter(None, [self.collection.name,
                                      self.field_of_research.code,
                                      self.field_of_research.description]))

    class Meta:
        db_table = 'applications_domain'


class FieldOfResearch(models.Model):
    """
    The `field of research <http://www.arc.gov.au/rfcd-seo-and-anzsic-codes>`_
    classification codes.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    code = models.CharField(
        max_length=6, unique=True, verbose_name='the FOR code',
        help_text='the code for the division/group/field')
    description = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='a human readable description of the division/group/field')

    def __str__(self):
        return " ".join([self.code, self.description])

    class Meta:
        db_table = 'applications_fieldofresearch'
        ordering = ['code']
        verbose_name_plural = "fields of research"


class Ingest(models.Model):
    """
    The daily readings of how much storage on a given storage product is used
    by the collection.

    **Note:** Not quite sure what to ditch/keep yet...

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    extraction_date = models.DateField(
        default=datetime.date.today,
        help_text='the date this data was read')
    allocated_capacity = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name='allocated capacity in GB',
        help_text='the allocated capacity in GB')
    used_capacity = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name='ingested capacity in GB',
        help_text='the ingested capacity in GB')
    collection = models.ForeignKey(
        'storage.Collection', models.DO_NOTHING,
        related_name='ingests',
        help_text='the collection associated with this reading')
    storage_product = models.ForeignKey(
        'storage.StorageProduct', models.DO_NOTHING,
        help_text='the storage product holding the data')
    used_replica = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        verbose_name='the replica storage used (if any) in GB',
        help_text='??')

    @property
    def ingested_tb(self):
        """The ingested amount in Terabytes"""
        return self.used_capacity / 1000

    @property
    def ingested_raw_tb(self):
        """Returns the raw ingested amount in Terabytes"""
        if self.id:
            used = self.used_capacity + self.used_replica
            scaled_used = used / self.storage_product.raw_conversion_factor
            return round(scaled_used / 1000, 4)
        else:
            return 0.0

    def __str__(self):
        return " ".join(filter(None,
                               [self.collection.name,
                                self.storage_product.product_name.value]))

    class Meta:
        db_table = 'applications_ingest'
        unique_together = ('extraction_date', 'collection', 'storage_product')
        indexes = [models.Index(
            fields=['collection', 'storage_product', 'extraction_date'])]


class Collection(models.Model):
    """
    The collection the data stored belongs to.

    Was "Project" in the VicNode system. The fields removed from the VicNode
    table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag
    * primary_data_source

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    # Todo: rename overview to 'notes'
    overview = models.TextField(
        blank=True, null=True,
        help_text='summary notes on the collection')
    name = models.TextField(
        verbose_name='Collection Name',
        help_text='the collection name')
    collective = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Collective'),
        default=GroupDefaultLabel('Collective'),
        related_name='collection_collective',
        help_text='legacy funding and is based on research domains')
    status = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Collection Status'),
        default=GroupDefaultLabel('Collection Status'),
        related_name='collection_status',
        help_text='the collection status')
    rifcs_consent = models.BooleanField(
        default=False,
        verbose_name='Metadata available to sponsoring institution',
        help_text='is the collection metadata to be made available to the '
                  'sponsoring institution?')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'applications_project'

    @property
    def application_code(self):
        """
        :return: the first application code to be shown as the collection code
        """
        allocation = self.allocations.first()
        return allocation.application.code if allocation else ' '

    def has_allocation_for_storage_products(self, storage_products):
        """
        :param storage_products: The suite of storage products to be tested
        :return: True if any of the storage products have an allocation,
                 otherwise False
        """
        return self.allocations.filter(
            storage_product__in=storage_products).count() > 0

    @property
    def for_count(self):
        """ :return: the number of FOR codes this collection covers"""
        return self.domains.count()

    @property
    def for_split(self):
        """ :return: the split percentage depending on number of FOR codes """
        if self.for_count == 0:
            return 1.0
        return round(1.0 / self.for_count, 4)

    @property
    def total_allocation(self):
        """ :return: the total allocation for the collection in Terabytes """
        result = self.allocations.exclude(size=None).aggregate(
            tot_alloc=Sum('size'))
        amount = result['tot_alloc']
        if amount:
            return amount / 1000
        return 0

    @property
    def for_amount(self):
        """ :return: the amount of the total allocation for each FOR code """
        return round(float(self.total_allocation) * float(self.for_split), 2)


class Request(models.Model):
    """
    A record of the original request received for the collection.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag
    * data_management_solution
    * operational_funding_source
    * estimated_duration
    * requested_start_date
    * project **NB:** A BOGUS field containing junk values!

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    # Todo: rename code to vicnode_id
    code = models.CharField(max_length=15, verbose_name='application code',
                            help_text='the application code')  # wtf is this?
    application_form = models.URLField(
        blank=True, null=True,
        help_text='a link to the original request document')
    notes = models.TextField(blank=True, null=True,
                             help_text='notes about this request')
    capital_funding_source = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Funding Code'),
        default=GroupDefaultLabel('Funding Code'),
        related_name='application_cap_funding_source',
        help_text='the funding scheme for the collection')
    institution = models.ForeignKey(
        'storage.Organisation', models.DO_NOTHING, blank=True, null=True,
        verbose_name='sponsoring institution',
        related_name='application_institution',
        help_text='the institution from which the request comes')
    # Todo: drop node
    node = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Node'),
        default=GroupDefaultLabel('Node'),
        blank=True, null=True,
        verbose_name='target node', related_name='Application_Node',
        help_text='VicNode or not?')
    # Todo: drop scheme
    scheme = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Allocation Scheme'),
        default=GroupDefaultLabel('Allocation Scheme'),
        verbose_name='allocation scheme',
        related_name='application_allocation_scheme',
        help_text='the scheme to be used for the collection')
    status = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Application Status'),
        default=GroupDefaultLabel('Application Status'),
        verbose_name='application status', related_name='application_status',
        help_text='where the request is in its lifecycle')
    faculty = models.ForeignKey(
        'storage.Suborganization', models.DO_NOTHING, blank=True, null=True,
        db_column='faculty_id',
        related_name='application_suborganization',
        help_text='the Faculty this request belongs to')

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'applications_request'


class StorageProductManager(models.Manager):
    def get_product_names(self):
        """
        :return: A queryset containing the storage product names as strings
        """
        return self.values_list('product_name__value', flat=True)

    def get_uom_product_names(self):
        """
        :return: A queryset containing the uom storage product names as strings
        """
        return self.filter(
            product_name__value__icontains='Melbourne').values_list(
            'product_name__value', flat=True)


class StorageProduct(models.Model):
    """
    The storage products that are/have been in use.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    unit_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='the cost per unit of storage')
    # Todo: drop operational_cost
    operational_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='the operation cost')
    capacity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='the total capacity of this storage product')
    raw_conversion_factor = models.DecimalField(
        max_digits=6, decimal_places=4, default=1,
        help_text='???')
    product_name = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Storage Product'),
        default=GroupDefaultLabel('Storage Product'),
        related_name='storageproduct_name',
        help_text='the name of this storage product')
    # Todo: drop scheme
    scheme = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Allocation Scheme'),
        default=GroupDefaultLabel('Allocation Scheme'),
        related_name='storageproduct_allocation_scheme',
        help_text='the allocation scheme for this product')
    operational_center = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Operational Center'),
        default=GroupDefaultLabel('Operational Center'),
        related_name='storage_product_op_center',
        help_text='this products operational center')

    objects = StorageProductManager()

    def __str__(self):
        return self.product_name.value

    class Meta:
        db_table = 'applications_storageproduct'


class Suborganization(models.Model):
    """
    The UoM Faculties. A storage request will be linked to a faculty.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag

    """
    id = models.AutoField(
        primary_key=True, help_text="the primary key")
    name = models.TextField(
        verbose_name='faculty',
        help_text='the full name of a UoM Faculty')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'applications_suborganization'
        verbose_name = 'Suborganization'
