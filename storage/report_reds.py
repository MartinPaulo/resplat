import logging
from collections import OrderedDict
from decimal import Decimal

from storage.models import Ingest, Collection, Request

# following constants are again hard coded label values... If the label is
# changed, the code breaks...
COMPUTATIONAL_STORAGE = ['Computational.Monash.Performance',
                         'Computational.Melbourne']

MELBOURNE_STORAGE = ['Computational.Monash.Performance',
                     'Computational.Melbourne',
                     'Market.Melbourne',
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
        sp_name = ingest.storage_product.product_name.value.strip()
        result[ingest.collection.id][sp_name] = ingest
    return result


def _column_name_index_map():
    """
    :return: An ordered dictionary, with the keys being the column names, and
             the values being the column index number
    """
    result = OrderedDict()
    result['Collection Name'] = 0
    result['Node ID'] = 1
    result['FOR 1'] = 2
    result['FOR 2'] = 3
    result['FOR 3'] = 4
    result['FOR 4'] = 5
    result['FOR 5'] = 6
    result['FOR 6'] = 7
    result['FOR 7'] = 8
    result['FOR 8'] = 9
    result['FOR 9'] = 10
    result['FOR 10'] = 11
    result['Research Data Approved (TB) [A]'] = 12
    result['Research Data Available(Ready) (TB) [B]'] = 13
    result['Total Storage Allocated (Committed) (TB) [C]'] = 14
    result['ReDS1/2 - Total Raw Disk Filled - SSD (TB) [D]'] = 15
    result['ReDS1/2 - Total Raw Disk Filled - Tier 1 (TB) [E]'] = 16
    result['ReDS1/2 - Total Raw Disk Filled - Tier 2/3 (TB) [F]'] = 17
    result['ReDS1/2 - Total Raw Tape Filled (TB) [G]'] = 18
    result['ReDS1/2 - Total Raw Storage Filled [H]'] = 19
    result['ReDS3 - Total Raw Disk Filled - SSD (TB) [D]'] = 20
    result['ReDS3 - Total Raw Disk Filled - Tier 1 (TB) [E]'] = 21
    result['ReDS3 - Total Raw Disk Filled - Tier 2/3 (TB) [F]'] = 22
    result['ReDS3 - Total Raw Tape Filled (TB) [G]'] = 23
    result['ReDS3 - Total Raw Storage Filled [H]'] = 24
    result['Total Cost [I]'] = 25
    result['% ingest completed'] = 26
    return result


def _allocation_totals(allocations, columns, storage_products, i_map):
    """
    :param allocations:
    :param columns: *mutated*
    :param storage_products:
    :param i_map:
    :return:
    """
    tier1_value = Decimal(0.0)
    total_used_value = Decimal(0.0)
    raw_alloc_map = {sp.product_name.value: Decimal(0.0) for sp in
                     storage_products}
    for allocation in allocations:
        storage_product = allocation.storage_product
        if storage_product in storage_products:
            sp_name = storage_product.product_name.value.strip()
            if sp_name in MELBOURNE_STORAGE:
                raw_alloc_map[
                    sp_name] += allocation.size_tb / storage_product.raw_conversion_factor
                if sp_name in COMPUTATIONAL_STORAGE:
                    tier1_value = tier1_value + allocation.size_tb / storage_product.raw_conversion_factor
                    total_used_value += allocation.size
            elif sp_name in ['Vault.Monash']:
                raw_alloc_map['Vault.Monash'] += allocation.size_tb * Decimal(
                    0.069)
                raw_alloc_map['Market.Monash'] += allocation.size_tb * Decimal(
                    2.0)
            elif sp_name in ['Market.Monash']:
                raw_alloc_map['Vault.Monash'] += allocation.size_tb * Decimal(
                    1.752)
                raw_alloc_map['Market.Monash'] += allocation.size_tb * Decimal(
                    1.752)
            columns[i_map['Total Cost [I]']] += allocation.capital_cost
    columns[i_map['Total Storage Allocated (Committed) (TB) [C]']] = sum(
        raw_alloc_map.values())  # Raw size - Total Allocation
    return tier1_value, total_used_value


def _ingest_totals(collection, filtered_ingests, total_used_value):
    tier23_value = Decimal(0.0)
    tape_value = Decimal(0.0)
    collection_ingests = filtered_ingests.get(collection.id)
    if collection_ingests:
        for storage_product_name in collection_ingests.keys():
            ingest = collection_ingests.get(storage_product_name)
            used_value = ingest.used_capacity
            if not used_value:
                continue
            storage_product = ingest.storage_product
            if storage_product_name not in COMPUTATIONAL_STORAGE:
                total_used_value += used_value
            if storage_product_name in ['Vault.Monash']:
                tier23_value += used_value * Decimal(0.069)
                tape_value += used_value * Decimal(2.0)
            elif storage_product_name in ['Market.Monash']:
                tier23_value += used_value * Decimal(1.752)
                tape_value += used_value * Decimal(1.752)
            elif storage_product_name in ['Vault.Melbourne.Object']:
                tape_value += used_value / storage_product.raw_conversion_factor
            elif storage_product_name in ['Market.Melbourne']:
                tier23_value += used_value / storage_product.raw_conversion_factor
    # convert GB to TerraBytes
    tier23_value = _get_tb_from_gb(tier23_value)
    tape_value = _get_tb_from_gb(tape_value)
    return tape_value, tier23_value, total_used_value


def _set_reds3_totals(columns, i_map, tape_value, tier1_value, tier23_value):
    columns[
        i_map['ReDS3 - Total Raw Disk Filled - Tier 1 (TB) [E]']] = tier1_value
    columns[i_map[
        'ReDS3 - Total Raw Disk Filled - Tier 2/3 (TB) [F]']] = tier23_value
    columns[i_map['ReDS3 - Total Raw Tape Filled (TB) [G]']] = tape_value
    # following doesn't ever appear to be set...
    zero = columns[i_map['ReDS3 - Total Raw Disk Filled - SSD (TB) [D]']]
    grand_total = zero + tier1_value + tier23_value + tape_value
    columns[i_map['ReDS3 - Total Raw Storage Filled [H]']] = grand_total


def _set_merit_totals(columns, i_map, tape_value, tier1_value, tier23_value):
    columns[i_map[
        'ReDS1/2 - Total Raw Disk Filled - Tier 1 (TB) [E]']] = tier1_value
    columns[i_map[
        'ReDS1/2 - Total Raw Disk Filled - Tier 2/3 (TB) [F]']] = tier23_value
    columns[i_map['ReDS1/2 - Total Raw Tape Filled (TB) [G]']] = tape_value
    # following doesn't ever appear to be set...
    zero = columns[i_map['ReDS1/2 - Total Raw Disk Filled - SSD (TB) [D]']]
    grand_total = zero + tier1_value + tier23_value + tape_value
    columns[i_map['ReDS1/2 - Total Raw Storage Filled [H]']] = grand_total


def _collection_for_codes(collection, columns, i_map):
    # Cols 2 thru 11, insert into columns at most 10 FOR codes for
    # this collection
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
    # put the column names at the top of the results being returned
    result.append(list(i_map.keys()))

    filtered_ingests = _latest_data_from_ingests(for_storage_products)

    for collection in Collection.objects.all().order_by('name'):
        if not collection.has_allocation_for_storage_products(
                for_storage_products):
            continue

        try:
            first_application = Request.objects.get(
                code=collection.application_code)
            status = first_application.status.value
            if first_application.scheme.value not in VALID_SCHEMES.values():
                continue
        except (Request.DoesNotExist, Request.MultipleObjectsReturned):
            logger.exception("First application not found?")
            continue  # Error, do not output record for this collection

        # default column values to 0
        columns = [0 for key in i_map]
        # here we only care the approved application
        if status == 'Approved':
            # Col 0 - Collection Name
            columns[i_map['Collection Name']] = collection.name
            # Col 1 - Collection Id, set to first application code
            columns[i_map['Node ID']] = first_application.code
            _collection_for_codes(collection, columns, i_map)
            # Col 12 - Total Allocation
            columns[i_map[
                'Research Data Approved (TB) [A]']] = collection.total_allocation

            tier1_value, total_used_value = _allocation_totals(
                collection.allocations.all(), columns, for_storage_products,
                i_map)

            tape_value, tier23_value, total_used_value = _ingest_totals(
                collection, filtered_ingests, total_used_value)

            columns[i_map[
                'Research Data Available(Ready) (TB) [B]']] = _get_tb_from_gb(
                total_used_value)

            if first_application.scheme.value == VALID_SCHEMES['Merit']:
                _set_merit_totals(columns, i_map, tape_value, tier1_value,
                                  tier23_value)
            elif first_application.scheme.value == VALID_SCHEMES['ReDS3']:
                _set_reds3_totals(columns, i_map, tape_value, tier1_value,
                                  tier23_value)

            if columns[i_map['Research Data Approved (TB) [A]']] > 0:
                # Col 26 - Percent Ingested'
                columns[i_map['% ingest completed']] = columns[i_map[
                    'Research Data Available(Ready) (TB) [B]']] / columns[
                                                           i_map[
                                                               'Research Data Approved (TB) [A]']]
            result.append(columns)

    return result
