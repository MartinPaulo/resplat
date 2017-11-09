import json
from decimal import Decimal
from operator import methodcaller

from storage.models import StorageProduct, Ingest, Domain


class ForCodeReportOptions:
    MELBOURNE = 'Melbourne'
    ALL = 'All'


MONASH_STORAGE_PRODUCTS = ['Computational.Monash.Performance', 'Vault.Monash',
                           'Market.Monash']
UOM_STORAGE_PRODUCTS = ['Computational.Melbourne', 'Market.Melbourne',
                        'Vault.Melbourne.Object']
ALL_STORAGE_PRODUCTS = MONASH_STORAGE_PRODUCTS + UOM_STORAGE_PRODUCTS


class ForCodeIngest(object):
    def __init__(self, for_code, code_desc='desc'):
        self.for_code = for_code
        self.code_desc = code_desc
        self.for_code_collection_list = []

    def add_collection(self, for_code_collection):
        self.for_code_collection_list.append(for_code_collection)

    def set_code_desc(self, code_desc):
        self.code_desc = code_desc

    def get_for_code_ingest_size(self):
        total_ingest_size = 0
        for for_code_collection in self.for_code_collection_list:
            total_ingest_size += for_code_collection.ingest_size
        return total_ingest_size / 1000

    def __repr__(self):
        return 'code: {} - desc: {} - ingest_size: {}'.format(
            self.for_code, self.code_desc, self.get_for_code_ingest_size())


class ForCodeCollection(object):
    def __init__(self, for_code, code_desc, collection_id, collection_name,
                 split, ingest_size):
        self.for_code = for_code
        self.code_desc = code_desc
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.split = split
        self.ingest_size = ingest_size

    def __repr__(self):
        return 'for code: {} - desc: {} - collection id: {} - ' \
               'collection name: {} - split: {} - ingest size: {}'.format(
            self.for_code, self.code_desc, self.collection_id,
            self.collection_name, self.split, self.ingest_size)


def _as_dict(for_code_ingests):
    """
    :param for_code_ingests: A list of ForCodeIngest instances
    :return: the for_code_ingests values in a dictionary
    """
    result = {}
    values = []
    for ingest in for_code_ingests:
        code = str(ingest.for_code)
        percentage = float(ingest.get_for_code_ingest_size())
        name = ingest.code_desc
        values.append(
            {"code": code, "percentage": percentage, "description": name})
    result['key'] = "FOR codes"
    result['values'] = values
    return [result]


def _trim_for_2_dig_code(for_code):
    return for_code[0:2]


def _is_two_digit_code(for_code):
    return len(for_code) == 2


def _sorted_for_code_ingests(for_code_ingest_dict, is_reverse_order):
    """
    sort the ForCodeIngest order based on the ingest size
    :param for_code_ingest_dict: a dictionary of ForCodeIngest
    :param is_reverse_order: is in reverser order
    :return: a sorted list of ForCodeIngest
    """
    for_code_ingest_list = list(for_code_ingest_dict.values())
    return sorted(for_code_ingest_list,
                  key=methodcaller('get_for_code_ingest_size'),
                  reverse=is_reverse_order)


def report_for_code_ingest(org_type):
    title = 'Data ingested split by 2-digit FOR code - '
    if org_type == ForCodeReportOptions.MELBOURNE:
        storage_products = UOM_STORAGE_PRODUCTS
        title += 'University of Melbourne'
    else:
        storage_products = ALL_STORAGE_PRODUCTS
        title += ForCodeReportOptions.ALL

    storage_products = list(
        StorageProduct.objects.filter(
            product_name__value__in=storage_products))

    collection_used_totals = {}
    # the latest Ingests based on the collection and storage product
    ingests = Ingest.objects.filter(
        storage_product__in=storage_products).values(
        'used_capacity', 'extraction_date', 'collection_id',
        'storage_product_id').order_by(
        'collection_id', 'storage_product_id', '-extraction_date').distinct(
        'collection_id', 'storage_product_id')
    for ingest in ingests:
        collection_id = ingest['collection_id']
        used_capacity = ingest['used_capacity']
        if used_capacity is None:  # legacy data can return None...
            used_capacity = Decimal(0.0)
        used_capacity += collection_used_totals.get(collection_id, 0)
        collection_used_totals[collection_id] = used_capacity

    for_code_ingests = {}
    domains = Domain.objects.all().order_by('field_of_research__code')
    for domain in domains:
        code = domain.field_of_research.code
        description = domain.field_of_research.description
        collection_id = domain.collection.id
        collection_name = domain.collection.name
        split_rate = domain.split
        collection_ingest_size = collection_used_totals.get(collection_id, 0)
        current_for_code_ingest_size = collection_ingest_size * split_rate
        for_code_collection = ForCodeCollection(code, description,
                                                collection_id,
                                                collection_name, split_rate,
                                                current_for_code_ingest_size)
        two_digit_code = _trim_for_2_dig_code(code)
        for_code_ingest = for_code_ingests.get(two_digit_code,
                                               ForCodeIngest(two_digit_code))
        for_code_ingest.add_collection(for_code_collection)
        if _is_two_digit_code(code):
            for_code_ingest.set_code_desc(description)
        for_code_ingests[two_digit_code] = for_code_ingest

    # sort in descending order based on the ingest size
    sorted_for_code_ingests = _sorted_for_code_ingests(for_code_ingests, True)
    # TODO: clean up so we only pass one sorted list across
    return {
        'title': title,
        'for_report_list': sorted_for_code_ingests,
        'for_percents': json.dumps(_as_dict(sorted_for_code_ingests))}
