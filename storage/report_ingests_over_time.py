import datetime
import json
from collections import OrderedDict
from operator import methodcaller

from django.db.models import Max, Min, Sum

from storage.models import Ingest


class StorageProductIngests(object):
    """
    Holds the ingest values over time for a storage product

    date_ranges: the date time ranges covered
    storage_product_name: the name of the storage product
    ingest_sums: an iterable of ingest sums for the storage product for each
                 day in the date range in date asc order
    """

    def __init__(self, storage_product_name, date_ranges, ingest_sums):
        self.storage_product_name = storage_product_name
        self.date_ranges = date_ranges
        self.ingest_sum_list = self._remove_zeros(ingest_sums)

    def __str__(self):
        return '{} - {}'.format(self.storage_product_name,
                                self.ingest_sum_list)

    @staticmethod
    def _remove_zeros(values):
        result = []
        prev_ingest_sum = 0
        for ingest_sum in values:
            # if the current days sum is 0 we just copy the previous days sum
            if ingest_sum != 0:
                prev_ingest_sum = ingest_sum
            else:
                ingest_sum = prev_ingest_sum
            result.append(float(ingest_sum))
        return result

    def total_size(self):
        """
        :return: the last ingest sum in the list of ingest sums
        """
        return self.ingest_sum_list[-1]

    def as_dict(self):
        """
        :return: the properties of the instance in a dictionary
        """
        result = {}
        values = []
        for index, item in enumerate(self.date_ranges):
            values.append([datetime.datetime(year=item.year, month=item.month,
                                             day=item.day).timestamp(),
                           self.ingest_sum_list[index]])
        result['key'] = self.storage_product_name
        result['values'] = values
        return result


def get_ingests_over_time():
    ingests_by_storage_product = _daily_ingests_grouped_by_storage_product()
    if not ingests_by_storage_product:
        return {'ingest_not_found': True}

    sorted_ingests_by_storage_product = sorted(ingests_by_storage_product,
                                               key=methodcaller('total_size'),
                                               reverse=True)

    # find the total size & start & end dates across all storage products
    sum_ingest_sizes = 0
    start_date = None
    end_date = None
    for storage_product_ingests in sorted_ingests_by_storage_product:
        if start_date is None:
            start_date = storage_product_ingests.date_ranges[0]
        if end_date is None:
            end_date = storage_product_ingests.date_ranges[-1]
        sum_ingest_sizes += storage_product_ingests.total_size()

    s_p_i_list = [s_p_i.as_dict() for s_p_i in ingests_by_storage_product]
    context = {'ingest_not_found': False,
               'sp_ingest_list': sorted_ingests_by_storage_product,
               'total_size': sum_ingest_sizes,
               'start_date': start_date,
               'end_date': end_date,
               'ingest_storage_products': json.dumps(s_p_i_list)}
    return context


def _get_date_ordered_dict_with_zero_values(start, end):
    """
    :param start: the start ingest date
    :param end: the end ingest date
    :return: an ordered dictionary - with time line date as key and 0 as value
    """
    time_gap = end - start
    if time_gap < datetime.timedelta(10):
        # if gap between start date and end date is less 10 days then we set
        # the gap as 15 days
        past10days_date = end - datetime.timedelta(days=10)
        dates = [past10days_date + datetime.timedelta(days=x) for x
                 in range(0, (end - past10days_date).days + 5)]
    else:
        dates = [start + datetime.timedelta(days=x) for x in
                 range(0, (end - start).days + 1)]
    return OrderedDict((date, 0) for (date) in dates)


def _daily_ingests_grouped_by_storage_product():
    # get the id's and names of all of the known storage products
    storage_products = Ingest.objects.values(
        'storage_product__id',
        'storage_product__product_name__value').distinct('storage_product')
    if not storage_products:
        return None

    # find the dates of the first and last ingests
    start_and_end = Ingest.objects.aggregate(Min('extraction_date'),
                                             Max('extraction_date'))
    results = []
    for storage_product in storage_products:
        daily_ingest_storage_product_sum = Ingest.objects.filter(
            storage_product__id=storage_product['storage_product__id']).values(
            'extraction_date', 'storage_product_id').annotate(
            ingest_size=Sum('used_capacity')).order_by('extraction_date')
        ingest_sum_dict = _get_date_ordered_dict_with_zero_values(
            start_and_end['extraction_date__min'],
            start_and_end['extraction_date__max'])
        for daily_sum in daily_ingest_storage_product_sum:
            extraction_date = daily_sum['extraction_date']
            ingest_sum_size = daily_sum['ingest_size']
            ingest_sum_dict[extraction_date] = ingest_sum_size / 1000
        results.append(StorageProductIngests(
            storage_product['storage_product__product_name__value'],
            [*ingest_sum_dict], ingest_sum_dict.values()))
    return results
