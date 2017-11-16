import logging
from collections import OrderedDict
from decimal import Decimal

from storage.models import Ingest, Collection, Request, StorageProduct, \
    CollectionProfile


class RedsReportOptions:
    MELBOURNE = 'Melbourne'  # only Melbourne storage products
    ALL = 'All'  # all storage products


class _ReportRow:
    """
    the values of a row in the report
    """
    # Description can be quite a long multi-line string...
    COLUMN_NAMES = ['Collection Name', 'Node ID', 'FOR 1', 'FOR 2',
                    'FOR 3', 'FOR 4', 'FOR 5', 'FOR 6', 'FOR 7', 'FOR 8',
                    'FOR 9', 'FOR 10', 'Research Data Approved (TB)',
                    'Research Data Available (Ready) (TB)',
                    'Total Storage Allocated (Committed) (TB)', 'Total Cost',
                    '% Ingest Completed',
                    'Data Custodian', 'Link', 'Description']

    def __init__(self):
        # following must be in the same order as the column names, as
        # get_values(...) returns their values in the order they are declared
        # ALSO: if you add/remove an attribute, it must have a corresponding
        # COLUMN_NAME entry added/removed
        self._collection_name = ''
        self._node_id = 0
        self._for_1 = 0
        self._for_2 = 0
        self._for_3 = 0
        self._for_4 = 0
        self._for_5 = 0
        self._for_6 = 0
        self._for_7 = 0
        self._for_8 = 0
        self._for_9 = 0
        self._for_10 = 0
        self._approved_tb = 0
        self._available_tb = 0
        self._committed_tb = 0
        self._total_cost = 0
        self._completed = 0
        self._custodian = ''
        self._link = ''
        self._description = ''

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, name):
        self._collection_name = name

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, value):
        self._node_id = value

    @property
    def approved_tb(self):
        return self._approved_tb

    @approved_tb.setter
    def approved_tb(self, value):
        self._approved_tb = value

    @property
    def available_tb(self):
        return self._available_tb

    @available_tb.setter
    def available_tb(self, value):
        self._available_tb = value

    @property
    def total_cost(self):
        return self._total_cost

    @total_cost.setter
    def total_cost(self, value):
        self._total_cost = value

    @property
    def committed_tb(self):
        return self._committed_tb

    @committed_tb.setter
    def committed_tb(self, value):
        self._committed_tb = value

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        self._completed = value

    @property
    def custodian(self):
        return self._custodian

    @custodian.setter
    def custodian(self, value):
        self._custodian = value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        self._link = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def set_for_code(self, code_number, value):
        """
        :param code_number: the FOR code number to set
        :param value: the value to set the FOR code to
        """
        setattr(self, '_for_%s' % code_number, value)

    def get_values(self):
        """
        :return: the values of the instance fields
        """
        return [value for value in self.__dict__.values()]


MARKET_MONASH = 'Market.Monash'
VAULT_MONASH = 'Vault.Monash'

# following constants are again hard coded label values... If the label is
# changed, the code breaks...

COMPUTATIONAL_STORAGE = ['Computational.Monash.Performance',
                         'Computational.Melbourne']

MELBOURNE_STORAGE = COMPUTATIONAL_STORAGE + ['Market.Melbourne',
                                             'Vault.Melbourne.Object']

VALID_SCHEMES = ['RDSI Merit', 'RDSI Board (ReDS3)']

logger = logging.getLogger(__name__)


def _get_tb_from_gb(size_in_gb):
    return size_in_gb / 1000


def _latest_data_from_ingests(storage_products):
    """
    :param storage_products: the service providers to filter ingests by
    :return: an ordered dict containing the ingests for each collection and
             storage product, again, in ordered dicts ordered by extraction
             date descending
    """
    result = OrderedDict()
    # find the set of Ingests based on the storage product list ordered latest
    # to earliest, distinct by collection id and storage product id
    ingests = Ingest.objects.filter(
        storage_product__in=storage_products).order_by(
        'collection_id', 'storage_product_id', '-extraction_date').distinct(
        'collection_id', 'storage_product_id')
    for ingest in ingests:
        if ingest.collection.id not in result:
            result[ingest.collection.id] = OrderedDict()
        storage_product_name = ingest.storage_product.product_name.value
        result[ingest.collection.id][storage_product_name] = ingest
    return result


def _allocation_totals(allocations, rr, storage_products):
    """
    :param allocations: the allocations to be summed
    :param rr: *mutated* the allocation sums are written into the report row
    :param storage_products: the storage products whose allocations are to be
                             summed
    :return: the sum of the allocation sizes
    """
    total_used = Decimal(0.0)
    raw_alloc = {sp.product_name.value: Decimal(0.0) for sp in
                 storage_products}
    for allocation in allocations:
        sp = allocation.storage_product
        if sp in storage_products:
            sp_name = sp.product_name.value
            if sp_name in MELBOURNE_STORAGE:
                raw_alloc[
                    sp_name] += allocation.size_tb / sp.raw_conversion_factor
                if sp_name in COMPUTATIONAL_STORAGE:
                    total_used += allocation.size
            elif sp_name in [VAULT_MONASH]:
                raw_alloc[VAULT_MONASH] += allocation.size_tb * Decimal(0.069)
                raw_alloc[MARKET_MONASH] += allocation.size_tb * Decimal(2.0)
            elif sp_name in [MARKET_MONASH]:
                raw_alloc[VAULT_MONASH] += allocation.size_tb * Decimal(1.752)
                raw_alloc[MARKET_MONASH] += allocation.size_tb * Decimal(1.752)
            rr.total_cost += allocation.capital_cost
    # Raw size - Total Allocation
    rr.committed_tb = sum(raw_alloc.values())
    return total_used


def _non_compute_ingests_used_capacity(collection, filtered_ingests):
    """
    :param collection: the collection whose ingests are to be summed
    :param filtered_ingests: the last ingests by storage product
    :return: the sum of the used capacity for non compute ingests
    """
    capacity_used = 0
    collection_ingests = filtered_ingests.get(collection.id)
    if collection_ingests:
        for storage_product_name in collection_ingests.keys():
            if storage_product_name in COMPUTATIONAL_STORAGE:
                continue
            ingest = collection_ingests.get(storage_product_name)
            if not ingest.used_capacity:
                continue
            capacity_used += ingest.used_capacity
    return capacity_used


def reds_123_calc(org_type):
    """
    REDS == 'Research E-Data Scheme'
    :param org_type: the organisations to return the report for
    :return: a list of rows containing the calculated reds 123 values for
             each collection that belongs to the org_type
    """
    result = [_ReportRow.COLUMN_NAMES]

    if RedsReportOptions.MELBOURNE == org_type:
        storage_products = StorageProduct.objects.filter(
            product_name__value__icontains='Melbourne')
    else:
        storage_products = StorageProduct.objects.all()

    filtered_ingests = _latest_data_from_ingests(storage_products)

    for collection in Collection.objects.all().order_by('name'):
        if not collection.has_allocation_for_storage_products(
                storage_products):
            continue

        try:
            request = Request.objects.get(code=collection.application_code)
            if not request or not request.status:
                continue
            status = request.status.value
            if request.scheme.value not in VALID_SCHEMES:
                continue
        except (Request.DoesNotExist, Request.MultipleObjectsReturned):
            logger.exception("Original request not found?")
            continue  # unexpected, so do not output a row for this collection

        # we only want data for the approved applications
        if status == 'Approved':
            # set all the initial column values to 0
            rr = _ReportRow()
            rr.collection_name = collection.name
            rr.node_id = request.code
            count = 0
            # fetch, at most 10, domains for the collection
            for domain in collection.domains.all()[:10]:
                count += 1
                rr.set_for_code(count, domain.field_of_research.code)
            rr.approved_tb = collection.total_allocation
            total_used = _allocation_totals(collection.allocations.all(),
                                            rr, storage_products)
            total_used += _non_compute_ingests_used_capacity(collection,
                                                             filtered_ingests)
            rr.available_tb = _get_tb_from_gb(total_used)
            if rr.approved_tb > 0:
                rr.completed = round(rr.available_tb / rr.approved_tb * 100, 2)
            rr.custodian = ", ".join(
                [c.full_name for c in collection.get_custodians()])
            rr.link = collection.link
            try:
                description = collection.collectionprofile.merit_justification
            except CollectionProfile.DoesNotExist:
                description = ''
            rr.description = description
            result.append(rr.get_values())

    return result
