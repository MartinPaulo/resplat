import logging
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from storage.csv_streamer import csv_stream
from storage.models import Ingest, StorageProduct, Collection
from storage.report_demographics import demographics_report
from storage.report_diff_reported_and_approved import \
    get_difference_between_approved_and_reported
from storage.report_for_code_ingest import report_for_code_ingest
from storage.report_funding import FundingReportForAllCollectionsBySP
from storage.report_ingests_over_time import get_ingests_over_time
from storage.report_reds import reds_123_calc
from storage.report_unfunded import UnfundedReportForAllCollections

logger = logging.getLogger(__name__)


@login_required
def ingests_for_week(request, days='0'):
    end_day = datetime.now().date() - timedelta(days=int(days))
    return render(request, 'weekly_stats.html',
                  _ingest_stats_for_week(request, end_day))


def _date_in_past(from_date, go_back_days):
    return from_date - timedelta(days=go_back_days)


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
    storage_products = StorageProduct.objects.get_by_name(
        list(products_of_interest.keys()))
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


@login_required
def reds_report_uom(request):
    uom_storage_products = StorageProduct.objects.filter(
        product_name__value__icontains='Melbourne')
    return csv_stream(reds_123_calc(uom_storage_products), 'reds123_uom.csv')


@login_required
def reds_report(request):
    all_storage_products = StorageProduct.objects.all()
    return csv_stream(reds_123_calc(all_storage_products), 'reds123_all.csv')


@login_required
def vicnode_funding_by_storage_product(request):
    funded = FundingReportForAllCollectionsBySP()
    context = {'funding': {'report': funded.report,
                           'type': funded.reportType,
                           'metric': {'text': funded.METRIC_TB,
                                      'factor': funded.get_conversion_factor(
                                          funded.METRIC_TB)}
                           }}
    return render(request, 'vicnode_funding_sp.html', context)


@login_required
def difference_between_reported_and_approved(request, target='All'):
    source = 'University of Melbourne' if target.lower() == 'melbourne' else target
    context = {
        'diff_list': get_difference_between_approved_and_reported(target),
        'source': source}
    return render(request, 'diff_reported_approved.html', context)


@login_required
def ingests_over_time(request):
    context = get_ingests_over_time()
    return render(request, 'ingests_over_time.html', context)


@login_required
def demographics_stream(request):
    """
    Export Demographics data
    :param request: http request
    :return: A CSV file with name 'demographics.csv'
    """
    return csv_stream(demographics_report(), 'demographics.csv')


@login_required
def unfunded_report(request):
    unfunded = UnfundedReportForAllCollections()
    context = {'funding': {'report': unfunded.report,
                           'type': unfunded.reportType,
                           'metric': {'text': unfunded.METRIC_GB,
                                      'factor': unfunded.get_conversion_factor(
                                          unfunded.METRIC_GB)}
                           }}
    return render(request, 'vicnode_unfunded.html', context)


@login_required
def for_code_ingest_uom(request):
    context = report_for_code_ingest('Melbourne')
    return render(request, 'for_percent_report.html', context)


@login_required
def for_code_ingest_all(request):
    context = report_for_code_ingest('All')
    return render(request, 'for_percent_report.html', context)
