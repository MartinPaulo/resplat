import datetime
from collections import OrderedDict
from operator import methodcaller

import matplotlib
import matplotlib.pyplot as plt
from django.db.models import Max, Min, Sum
from matplotlib.dates import DateFormatter
from matplotlib.patches import Rectangle

from resplat.settings import MEDIA_ROOT
from storage.models import Ingest


class StorageProductIngest(object):
    """
    Holds the total ingest over time for a storage product
    date_ranges: the date time ranges
    sp_name: a storage product name
    ingest_sum_list:  a ingest sum list which hold the each date ingest over
                      time in date asc order
    """

    def __init__(self, storage_product_name, date_ranges, ingest_sum_list):
        self.sp_name = storage_product_name
        self.date_ranges = date_ranges
        self.ingest_sum_list = ingest_sum_list

    def __str__(self):
        return '{} - {}'.format(self.sp_name, self.ingest_sum_list)

    def total_size(self):
        return self.ingest_sum_list[-1]


def get_total_ingests_over_time():
    ingest_storage_product_list = _daily_ingests_grouped_by_storage_product()
    if not ingest_storage_product_list:
        return {'ingest_not_found': True}
    image_path = '/report_graph/' + 'total_ingest_over_time.png'
    chart_path = MEDIA_ROOT + image_path
    sorted_sp_ingest_list = sorted(ingest_storage_product_list,
                                   key=methodcaller('total_size'),
                                   reverse=True)
    _draw_ingest_stacked_graph(sorted_sp_ingest_list, chart_path)

    # calculate the total size for all storage products
    total_sp_ingest_size = 0
    start_date = None
    end_date = None

    for sp_ingest in sorted_sp_ingest_list:
        if start_date is None:
            start_date = sp_ingest.date_ranges[0]
        if end_date is None:
            end_date = sp_ingest.date_ranges[-1]
        total_sp_ingest_size += sp_ingest.total_size()

    context = {'ingest_not_found': False,
               'sp_ingest_list': sorted_sp_ingest_list,
               'total_size': total_sp_ingest_size, 'start_date': start_date,
               'end_date': end_date,
               'image': image_path}
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
    storage_products = Ingest.objects.values(
        'storage_product__id',
        'storage_product__product_name__value').distinct('storage_product')
    if not storage_products:
        return None

    start_and_end = Ingest.objects.aggregate(Min('extraction_date'),
                                             Max('extraction_date'))
    results = []
    for storage_product in storage_products:
        storage_product_id = storage_product['storage_product__id']
        daily_ingest_storage_product_sum = Ingest.objects.filter(
            storage_product__id=storage_product_id).values(
            'extraction_date', 'storage_product_id').annotate(
            ingest_size=Sum('used_capacity')).order_by('extraction_date')
        ingest_sum_dict = _get_date_ordered_dict_with_zero_values(
            start_and_end['extraction_date__min'],
            start_and_end['extraction_date__max'])
        for daily_sum in daily_ingest_storage_product_sum:
            extraction_date = daily_sum['extraction_date']
            ingest_sum_size = daily_sum['ingest_size']
            ingest_sum_dict[extraction_date] = ingest_sum_size / 1000
        values = []
        prev_ingest_sum = 0
        for ingest_sum in ingest_sum_dict.values():
            # if the current day's sum is zero we just copy the previous day's
            if ingest_sum != 0:
                prev_ingest_sum = ingest_sum
            else:
                ingest_sum = prev_ingest_sum
            values.append(float(ingest_sum))
        # create the StorageProductIngest
        store_product_ingest = StorageProductIngest(
            storage_product['storage_product__product_name__value'],
            [*ingest_sum_dict], values)
        results.append(store_product_ingest)
    return results


dark_orange = [1, 140 / 255, 0]
dark_golden_rod = [184 / 255, 134 / 255, 11 / 255]
yellow_green = [154 / 255, 205 / 255, 50 / 255]
olive_green = [107 / 255, 142 / 255, 35 / 255]
lime_green = [50 / 255, 205 / 255, 50 / 255]
medium_sea_green = [60 / 255, 179 / 255, 113 / 255]
forest_green = [34 / 255, 139 / 255, 34 / 255]
light_sea_green = [32 / 255, 178 / 255, 170 / 255]
cadet_blue = [95 / 255, 158 / 255, 160 / 255]
royal_blue = [65 / 255, 105 / 255, 225 / 255]
corn_flower_blue = [100 / 255, 149 / 255, 237 / 255]
light_pink = [1, 182 / 255, 193 / 255]
blue_violet = [138 / 255, 43 / 255, 226 / 255]
dark_slate_blue = [72 / 255, 61 / 255, 139 / 255]
medium_purple = [147 / 255, 112 / 255, 219 / 255]
dark_magenta = [139 / 255, 0, 139 / 255]
medium_orchid = [186 / 255, 85 / 255, 211 / 255]
chocolate = [210 / 255, 105 / 255, 30 / 255]
dark_cyan = [0, 139 / 255, 139 / 255]
blue = [0, 0, 128 / 255]
dark_red = [139 / 255, 0, 0]
floral_white = [1, 250 / 255, 240 / 255]
peru = [205 / 255, 133 / 255, 63 / 255]
dark_slate_gray = [47 / 255, 79 / 255, 79 / 255]

ALL_COLORS = [dark_orange,
              dark_golden_rod,
              yellow_green,
              olive_green,
              lime_green,
              medium_sea_green,
              forest_green,
              light_sea_green,
              cadet_blue,
              royal_blue,
              corn_flower_blue,
              light_pink,
              blue_violet,
              dark_slate_blue,
              medium_purple,
              dark_magenta,
              medium_orchid,
              chocolate,
              dark_cyan,
              blue,
              dark_red,
              floral_white,
              peru,
              dark_slate_gray
              ]


def _draw_ingest_stacked_graph(storage_product_ingest_list, save_path):
    matplotlib.use('TkAgg')
    fig = plt.figure()
    fig.set_size_inches(14.5, 10, forward=True)
    ax1 = fig.add_subplot(1, 1, 1)
    legend_labels = []
    date_time_lines = []
    sp_graph_ydata_list = []

    for sp_ingest in storage_product_ingest_list:
        sp_name = sp_ingest.sp_name
        legend_labels.append(sp_name)
        ingest_sum_list = sp_ingest.ingest_sum_list
        if len(date_time_lines) == 0:
            date_time_lines = sp_ingest.date_ranges
        sp_graph_ydata_list.append(ingest_sum_list)

    colors = ALL_COLORS[:len(legend_labels)]
    # make the stack plot
    stack_pcs = ax1.stackplot(date_time_lines, sp_graph_ydata_list,
                              colors=colors)
    # set the date time line x tick labels
    ax1.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
    ax1.grid(True)  # set background grid lines
    fig.autofmt_xdate()  # make the fig update
    # make proxy artists for legend
    proxy_rects = [Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in
                   stack_pcs]
    # make the legend
    ax1.legend(proxy_rects, legend_labels, bbox_to_anchor=(-0.04, 0.2),
               fontsize=10)
    plt.title('Total VicNode Ingest Over Time')
    plt.ylabel('TBytes')
    plt.xlabel('Date')

    plt.savefig(save_path, bbox_inches='tight')
    # note: remember plt.clf() to clear buffer
    plt.clf()
    plt.close()
