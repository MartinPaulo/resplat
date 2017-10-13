import logging
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from storage.models import Ingest, StorageProduct, Collection, Label

logger = logging.getLogger(__name__)


@login_required
def ingests_for_week(request, days='0'):
    end_day = datetime.now().date() - timedelta(days=int(days))
    return render(request, 'weekly_stats.html',
                  _ingest_stats_for_week(request, end_day))


def _date_in_past(from_date, go_back_days):
    return from_date - timedelta(days=go_back_days)


def _get_storage_products(product_names):
    """
    :return: the storage products in a dictionary keyed by their name
    """
    results = {}
    sp = StorageProduct.objects.filter(product_name__value__in=product_names)
    for product in sp:
        results[product.product_name.value] = product
    return results


def _ingest_counts_for_date(ingest_date, storage_products):
    ingested = {}
    for name, storage_product in storage_products.items():
        count = Ingest.objects.filter(storage_product=storage_product,
                                      extraction_date=ingest_date).count()
        ingested[name] = count > 0
    return {
        'ingested': ingested,
    }


def _ingest_stats_for_week(request, end_date):
    # brittle as the products of interest must match the labels in the database
    products_of_interest = {
        'Computational.Melbourne': 'UoMC',
        'Market.Melbourne': 'UoMM',
        'Vault.Melbourne.Object': 'UoMV'
    }
    storage_products = _get_storage_products(list(products_of_interest.keys()))
    week_data = []
    for days_past in range(0, 7):
        target_day = _date_in_past(end_date, days_past)
        counts = _ingest_counts_for_date(target_day, storage_products)
        ingest_status = {}
        for key, value in products_of_interest.items():
            ingest_status[value] = counts['ingested'][key] if key in counts[
                'ingested'] else False
        week_data.append({'date': target_day.strftime('%d %b %Y'),
                          'stats': ingest_status})
    return {
        'products': products_of_interest,
        'current_date': (end_date.strftime('%d %b %Y')),
        'week_data': week_data
    }


def _fetch_collection_status_data():
    result = []
    last_status = None
    current_status_collection_list = []
    for collection in Collection.objects.all().order_by('status'):
        if last_status != collection.status:
            if not last_status and len(current_status_collection_list):
                # we have a list of collections with no status set on them
                result.append(
                    {'status': None,
                     'collection_list': current_status_collection_list})
            last_status = collection.status
            current_status_collection_list = []
            result.append(
                {'status': collection.status,
                 'collection_list': current_status_collection_list})
        current_status_collection_list.append(collection)
    return result


@login_required
def collection_status(request):
    report_list = _fetch_collection_status_data()
    context = {'report_list': report_list}
    return render(request, 'collection_status.html', context)
