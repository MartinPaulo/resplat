import logging
from collections import OrderedDict
from decimal import Decimal

from storage.models import Ingest, Collection, Request

# following are the column names of the output rows
COLLECTION_NAME = 'Collection Name'
NODE_ID = 'Node ID'
APPROVED_TB = 'Research Data Approved (TB)'
AVAILABLE_TB = 'Research Data Available (Ready) (TB)'
COMMITTED_TB = 'Total Storage Allocated (Committed) (TB)'
COMPLETED = '% ingest completed'
TOTAL_COST = 'Total Cost'

MARKET_MONASH = 'Market.Monash'
VAULT_MONASH = 'Vault.Monash'

# following constants are again hard coded label values... If the label is
# changed, the code breaks...

COMPUTATIONAL_STORAGE = ['Computational.Monash.Performance',
                         'Computational.Melbourne']

MELBOURNE_STORAGE = COMPUTATIONAL_STORAGE + ['Market.Melbourne',
                                             'Vault.Melbourne.Object']

VALID_SCHEMES = {'Merit': 'RDSI Merit', 'ReDS3': 'RDSI Board (ReDS3)'}

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
        storage_product_name = ingest.storage_product.product_name.value.strip()
        result[ingest.collection.id][storage_product_name] = ingest
    return result


def _column_name_index_map():
    """
    :return: An ordered dictionary, with the keys being the column names, and
             the values being the column index number
    """
    result = OrderedDict()
    column_names = [COLLECTION_NAME, NODE_ID, 'FOR 1', 'FOR 2', 'FOR 3',
                    'FOR 4', 'FOR 5', 'FOR 6', 'FOR 7', 'FOR 8', 'FOR 9',
                    'FOR 10', APPROVED_TB, AVAILABLE_TB,
                    COMMITTED_TB, TOTAL_COST, COMPLETED]
    for i, name in enumerate(column_names):
        result[name] = i
    return result


def _allocation_totals(allocations, columns, storage_products, i_map):
    """
    :param allocations: the allocations to be summed
    :param columns: *mutated* the allocation sums are written into the columns
    :param storage_products: the storage products whose allocations are to be
                             summed
    :param i_map: a map of column names and their index values
    :return: the sum of the allocation sizes
    """
    total_used = Decimal(0.0)
    raw_alloc_map = {sp.product_name.value: Decimal(0.0) for sp in
                     storage_products}
    for allocation in allocations:
        storage_product = allocation.storage_product
        if storage_product in storage_products:
            storage_product_name = storage_product.product_name.value.strip()
            if storage_product_name in MELBOURNE_STORAGE:
                raw_alloc_map[
                    storage_product_name] += allocation.size_tb / storage_product.raw_conversion_factor
                if storage_product_name in COMPUTATIONAL_STORAGE:
                    total_used += allocation.size
            elif storage_product_name in [VAULT_MONASH]:
                raw_alloc_map[VAULT_MONASH] += allocation.size_tb * Decimal(
                    0.069)
                raw_alloc_map[MARKET_MONASH] += allocation.size_tb * Decimal(
                    2.0)
            elif storage_product_name in [MARKET_MONASH]:
                raw_alloc_map[VAULT_MONASH] += allocation.size_tb * Decimal(
                    1.752)
                raw_alloc_map[MARKET_MONASH] += allocation.size_tb * Decimal(
                    1.752)
            columns[i_map[TOTAL_COST]] += allocation.capital_cost
    # Raw size - Total Allocation
    columns[i_map[COMMITTED_TB]] = sum(raw_alloc_map.values())
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


def _get_collection_for_codes(collection, columns, i_map):
    """
    :param collection: the source collection
    :param columns: *mutated* the for code values are written into the columns
    :param i_map: a map of column names and their index values
    """
    count = 0
    # fetch, at most 10, domains for the collection
    for domain in collection.domains.all()[:10]:
        count += 1
        columns[i_map['FOR %s' % count]] = domain.field_of_research.code


def reds_123_calc(for_storage_products):
    """
    :param for_storage_products: the list of storage products to calculate for
    :return: a list of rows containing the calculated reds 123 values for
             each collection that uses one of the storage products in the
             parameter
    """
    result = []
    i_map = _column_name_index_map()
    # put the column names as the first row of the results being returned
    result.append(list(i_map.keys()))

    filtered_ingests = _latest_data_from_ingests(for_storage_products)

    for collection in Collection.objects.all().order_by('name'):
        if not collection.has_allocation_for_storage_products(
                for_storage_products):
            continue

        try:
            request = Request.objects.get(code=collection.application_code)
            if not request or not request.status:
                continue
            status = request.status.value
            if request.scheme.value not in VALID_SCHEMES.values():
                continue
        except (Request.DoesNotExist, Request.MultipleObjectsReturned):
            logger.exception("Original request not found?")
            continue  # unexpected, so do not output a row for this collection

        # we only want data for the approved applications
        if status == 'Approved':
            # set all the column values to 0
            columns = [0 for key in i_map]
            columns[i_map[COLLECTION_NAME]] = collection.name
            columns[i_map[NODE_ID]] = request.code
            _get_collection_for_codes(collection, columns, i_map)
            columns[i_map[APPROVED_TB]] = collection.total_allocation
            total_used = _allocation_totals(collection.allocations.all(),
                                            columns, for_storage_products,
                                            i_map)
            total_used += _non_compute_ingests_used_capacity(collection,
                                                             filtered_ingests)
            columns[i_map[AVAILABLE_TB]] = _get_tb_from_gb(total_used)
            if columns[i_map[APPROVED_TB]] > 0:
                columns[i_map[COMPLETED]] = round(
                    columns[i_map[AVAILABLE_TB]] / columns[
                        i_map[APPROVED_TB]] * 100,
                    2)
            result.append(columns)

    return result
