from decimal import *
from operator import methodcaller

from matplotlib import pyplot as plt

from resplat.settings import MEDIA_ROOT
from storage.models import StorageProduct, Ingest, Domain
from storage.report_total_ingest_over_time import ALL_COLORS

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


def report_for_code_ingest(org_type):
    title = 'Data ingested split by 2-digit FOR code - '
    if org_type == 'Melbourne':
        storage_products = UOM_STORAGE_PRODUCTS
        title += 'University of Melbourne'
    else:
        storage_products = ALL_STORAGE_PRODUCTS
        title += 'All'

    storage_products = list(
        StorageProduct.objects.filter(
            product_name__value__in=storage_products))

    collection_used_size_dict = {}
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
        found_ingest_size = collection_used_size_dict.get(collection_id)
        if not found_ingest_size:
            found_ingest_size = used_capacity
        else:
            found_ingest_size += used_capacity
        collection_used_size_dict[collection_id] = found_ingest_size

    for_code_ingest_dict = {}
    domains = Domain.objects.all().order_by('field_of_research__code')
    for domain in domains:
        code = domain.field_of_research.code
        description = domain.field_of_research.description
        collection_id = domain.collection.id
        collection_name = domain.collection.name
        split_rate = domain.split
        col_ingest_size = collection_used_size_dict.get(collection_id)
        if not col_ingest_size:  # can return null from the db...
            col_ingest_size = 0
        current_for_code_ingest_size = col_ingest_size * split_rate
        for_code_collection = ForCodeCollection(code, description,
                                                collection_id,
                                                collection_name, split_rate,
                                                current_for_code_ingest_size)
        two_digit_code = _trim_for_2_dig_code(code)
        for_code_ingest = for_code_ingest_dict.get(two_digit_code,
                                                   ForCodeIngest(
                                                       two_digit_code))
        for_code_ingest.add_collection(for_code_collection)
        if _is_two_digit_code(code):
            for_code_ingest.set_code_desc(description)
        for_code_ingest_dict[two_digit_code] = for_code_ingest

    # sort the ForCodeIngest Dictionary in Des order based on the Ingest size
    for_code_ingest_list = _sorted_for_code_ingests(for_code_ingest_dict, True)
    image_path = '/report_graph/' + org_type + '.png'
    chart_path = MEDIA_ROOT + image_path
    _draw_pie_chart(for_code_ingest_list, title, chart_path)
    return {'image': image_path, 'title': title,
            'for_report_list': for_code_ingest_list}


def _trim_for_2_dig_code(for_code):
    return for_code[0:2]


def _is_two_digit_code(for_code):
    return len(for_code) == 2


def _draw_pie_chart(for_code_ingest_list, title, save_path):
    code_labels = []
    code_split_ingests = []

    for ingest in for_code_ingest_list:
        for_code = ingest.for_code
        for_desc = ingest.code_desc
        size = ingest.get_for_code_ingest_size()
        code_split_ingests.append(size)
        code_labels.append(
            '{0} - {1} - {2:1.4f} TB'.format(for_code, for_desc, size))
    code_size = len(for_code_ingest_list)
    colors = ALL_COLORS[0:code_size]
    total_ingest_size = sum(code_split_ingests)

    code_ingest_percentages = []
    for ingest in code_split_ingests:
        percentage = ingest / total_ingest_size * Decimal(100)
        code_ingest_percentages.append(percentage)

    patches, texts = plt.pie(code_split_ingests, colors=colors, startangle=90,
                             radius=1.2)
    labels = ['{0} - {1:1.2f} %'.format(i, j) for i, j in
              zip(code_labels, code_ingest_percentages)]

    plt.legend(patches, labels, loc='center left', bbox_to_anchor=(-0.7, 0.5),
               fontsize=8)
    plt.title(title, fontsize=8)
    plt.axis('equal')
    plt.savefig(save_path, bbox_inches='tight')
    # note: remember plt.clf() to clear buffer
    plt.clf()
    plt.close()


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
