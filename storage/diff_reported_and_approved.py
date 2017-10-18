from storage.models import Allocation, Ingest

__author__ = 'simonyu'

from django.db.models import Sum


class DiffReportedAndApprovedResult(object):
    """
        A difference between reported allocation and approved allocation
    """

    def __init__(self, ingest, approved_size, reported_size):
        self.ingest = ingest
        self.approved_size = approved_size
        self.reported_size = reported_size
        # always approved total size - reported size, if result is
        # negative result which means it over size
        self.diff_size = approved_size - reported_size

    def __repr__(self):
        return '{} - {} reported : {} -- approved : {} - diff size {}'.format(
            self.ingest.collection.name,
            self.ingest.storage_product.product_name,
            self.ingest.allocated_capacity,
            self.approved_size,
            self.diff_size)


def _last_ingest_for_collection_and_storage_product(collection_id,
                                                    storage_product_id):
    return Ingest.objects.filter(
        collection__id=collection_id,
        storage_product__id=storage_product_id).order_by(
        '-extraction_date').first()


def get_difference_between_approved_and_reported(organization):
    """
    :param organization: if 'melbourne' then results are only for melbourne
                         otherwise for all organizations
    :return: the difference between allocations approved and reported sizes,
             ordered by largest to smallest
    """
    if organization.lower() == 'melbourne':
        approved_allocations = Allocation.objects.filter(
            storage_product__product_name__value__icontains="Melbourne").values(
            'collection_id', 'storage_product_id').annotate(
            approved_total_size=Sum('size')).order_by('collection_id')
    else:
        approved_allocations = Allocation.objects.values(
            'collection_id', 'storage_product_id').annotate(
            approved_total_size=Sum('size')).order_by(
            'collection_id')

    differences = []
    for allocation in approved_allocations:
        approved_size = allocation['approved_total_size']
        if approved_size != 0:
            ingest = _last_ingest_for_collection_and_storage_product(
                allocation['collection_id'],
                allocation['storage_product_id'])
            if ingest is not None:
                reported_size = 0
                if ingest.allocated_capacity:
                    reported_size = ingest.allocated_capacity
                if reported_size != approved_size:
                    differences.append(DiffReportedAndApprovedResult(
                        ingest, approved_size, reported_size))
    return sorted(differences, key=lambda x: x.diff_size, reverse=True)
