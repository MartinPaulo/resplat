from storage.models import Allocation, Ingest

__author__ = 'simonyu'

from django.db.models import Sum


class DiffReportedAndApprovedResult(object):
    """
        A difference between reported allocation and approved allocation
    """

    def __init__(self, ingest, approved_size, diff_size):
        self.ingest = ingest
        self.approved_size = approved_size
        self.diff_size = diff_size

    def __repr__(self):
        return '{} - {} reported : {} -- approved : {} - diff size {}'.format(
            self.ingest.collection.name,
            self.ingest.storage_product.product_name,
            self.ingest.allocated_capacity,
            self.approved_size,
            self.diff_size)


def fetch_diff_reported_and_approved_allocation(org_type):
    if org_type.lower() == 'monash':
        approved_allocs = Allocation.objects.filter(
            storage_product__product_name__value__icontains="Monash").values(
            'collection_id', 'storage_product_id').annotate(
            approved_total_size=Sum('size')).order_by('collection_id')
    elif org_type.lower() == 'melbourne':
        approved_allocs = Allocation.objects.filter(
            storage_product__product_name__value__icontains="Melbourne").values(
            'collection_id', 'storage_product_id').annotate(
            approved_total_size=Sum('size')).order_by('collection_id')
    else:
        approved_allocs = Allocation.objects.values('collection_id',
                                                    'storage_product_id').annotate(
            approved_total_size=Sum('size')).order_by(
            'collection_id')

    allocations_diffs = []
    for dic in approved_allocs:
        approved_total_size = dic['approved_total_size']
        col_id = dic['collection_id']
        storage_prod_id = dic['storage_product_id']
        if approved_total_size != 0:
            ingest = query_latest_ingest_base_on_collection_and_storage_product(
                col_id,
                storage_prod_id)
            if ingest is not None:
                reported_size = 0
                if ingest.allocated_capacity:
                    reported_size = ingest.allocated_capacity
                if reported_size != approved_total_size:
                    # always approved total size - reported size, if result is
                    # negative result which means it over size
                    diff_size = approved_total_size - reported_size
                    diff_reported_approved_result = DiffReportedAndApprovedResult(
                        ingest, approved_total_size, diff_size)
                    allocations_diffs.append(diff_reported_approved_result)

    # return sorted by size of difference biggest to smallest
    return sorted(allocations_diffs, key=lambda
        diff_reported_approved_result: diff_reported_approved_result.diff_size,
                  reverse=True)


def query_latest_ingest_base_on_collection_and_storage_product(collection_id,
                                                               storage_prod_id):
    ingest = Ingest.objects.filter(collection__id=collection_id,
                                   storage_product__id=storage_prod_id).order_by(
        '-extraction_date')
    found_size = ingest.count()
    if found_size > 0:
        return ingest[0]
    else:
        return None
