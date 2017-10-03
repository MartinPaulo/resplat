import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from storage.models import Ingest, Label, StorageProduct

logger = logging.getLogger(__name__)


@login_required
def ingests_for_week(request, days='0'):
    end_day = datetime.now().date() - timedelta(days=int(days))
    return render(request, 'weekly_stats.html',
                  _ingest_stats_for_week(request, end_day))


def _date_in_past(from_date, go_back_days):
    return from_date - timedelta(days=go_back_days)


def _get_storage_products():
    """
    :return: the storage products in a dictionary keyed by their name (which
             is taken from the labels table)
    """
    # below is brittle: if you change the value in the database...
    group_label = Label.objects.get(value='Storage Product',
                                    group__value='Label')
    results = {}
    for label in Label.objects.filter(group=group_label):
        try:
            results[label.value] = StorageProduct.objects.get(
                product_name=label)
        except (StorageProduct.DoesNotExist,
                StorageProduct.MultipleObjectsReturned):
            logger.exception("Unexpected error on fetching storage products")
    return results


def _ingest_counts_for_date(ingest_date, storage_products):
    ingested = {}
    errors = []
    for name, storage_product in storage_products.items():
        try:
            count = Ingest.objects.filter(storage_product=storage_product,
                                          extraction_date=ingest_date).count()
            ingested[name] = count > 0
        except Exception as e:
            errors.append(e)
    return {
        'ingested': ingested,
        'errors': errors
    }


def _ingest_stats_for_week(request, end_date):
    # brittle as the products of interest must match the labels in the database
    products_of_interest = {
        'Computational.Melbourne': 'UoMC',
        'Market.Melbourne': 'UoMM',
        'Vault.Melbourne': 'UoMV'
    }
    storage_products = _get_storage_products()
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
        for exception in counts['errors']:
            messages.add_message(request, messages.WARNING, exception)
    return {
        'products': products_of_interest,
        'current_date': (end_date.strftime('%d %b %Y')),
        'week_data': week_data
    }
