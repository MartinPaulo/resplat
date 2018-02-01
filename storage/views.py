import logging
from datetime import datetime, timedelta
from urllib.parse import unquote

from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

from storage.csv_streamer import csv_stream
from storage.forms import CollectionsSearchForm
from storage.models import Ingest, StorageProduct, Collection, \
    CollectionProfile, Allocation, Request, Contact
from storage.report_demographics import demographics_report
from storage.report_diff_reported_and_approved import \
    get_difference_between_approved_and_reported
from storage.report_for_code_ingest import report_for_code_ingest, \
    ForCodeReportOptions
from storage.report_funding import FundingReportForAllCollectionsBySP, \
    FundingReportForCollection
from storage.report_ingests_over_time import get_ingests_over_time
from storage.report_reds import reds_123_calc, RedsReportOptions
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
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    try:
        collection_profile = CollectionProfile.objects.get(
            collection=collection_id)
    except CollectionProfile.DoesNotExist:
        collection_profile = None
    allocations = Allocation.objects.order_by().filter(
        collection=collection_id).values(
        'application__code',
        'application__institution__name__value',
        'application__scheme__value',
        'application__status__value').distinct()
    funding_report = FundingReportForCollection(collection)

    context = {'collection': collection,
               'collection_profile': collection_profile,
               'allocations': allocations,
               'funding': {
                   'report': funding_report.report,
                   'type': funding_report.reportType,
                   'metric': {'text': funding_report.METRIC_GB,
                              'factor': funding_report.get_conversion_factor(
                                  funding_report.METRIC_GB)}
               }
               }
    return render(request, 'collection_detail.html', context=context)


def _or(_left, _right, _type):
    result = _left  # default to left
    if isinstance(_left, _type) and isinstance(_right, _type):
        # if both are of the same type then or them together
        result = _left | _right
    elif _left is None:
        # otherwise, if there is no left, default to right
        result = _right
    return result


def _plus(_left, _right, _type):
    result = _left  # default to left
    if isinstance(_left, _type) and isinstance(_right, _type):
        # if both are of the same type then add them together
        result = _left + _right
    elif _left is None:
        # otherwise, if there is no left, default to right
        result = _right
    return result


def _search_cacheable(name, code):
    key = name + code
    # Is this result session specific?
    result = cache.get(key)
    if not result:
        query = None
        vector = None
        if name:
            query = SearchQuery(name)
            vector = SearchVector('name')
        if code:
            query = _or(query, SearchQuery(code), SearchQuery)
            vector = _plus(vector,
                           SearchVector('allocations__application__code'),
                           SearchVector)
        if query is not None:
            collections = Collection.objects.annotate(search=vector).filter(
                search=query).order_by('name', 'id').distinct('name', 'id')
        else:
            collections = Collection.objects.all().order_by('name')
        result = list(collections)
        cache.set(key, result)
    return result


@login_required
def collection_index(request):
    name = ''
    code = ''
    if request.method == 'POST':
        form = CollectionsSearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            code = form.cleaned_data['code']
    else:
        name = unquote(request.GET.get('name', ''))
        code = unquote(request.GET.get('code', ''))
        form = CollectionsSearchForm(initial={'name': name, 'code': code})
    collections = _search_cacheable(name, code)
    paginator = Paginator(collections, 25, orphans=4)
    page_wanted = request.GET.get('page', 1)
    try:
        collections = paginator.page(page_wanted)
    except PageNotAnInteger:  # If page is not an integer, deliver first page
        collections = paginator.page(1)
    except EmptyPage:  # If page is out of range, deliver last page
        collections = paginator.page(paginator.num_pages)
    context = {'latest_collection_list': collections, 'form': form,
               'name': name, 'code': code}
    return render(request, 'collection_index.html', context)


@login_required
def application_detail(request, application_code):
    application = get_object_or_404(Request, code=application_code)
    allocations = Allocation.objects.all().filter(
        application__code=application_code)

    return render(request, 'application_detail.html',
                  {'application': application, 'allocations': allocations})


@login_required
def contact_detail(request, contact_id):
    collections = []
    contact = get_object_or_404(Contact, pk=contact_id)
    for collection in Collection.objects.filter(
            custodians__person=contact).all():
        if collection not in collections:
            collections.append(collection)
    return render(request, 'contact_detail.html',
                  {'contact': contact, 'collections': collections})


@login_required
def reds_report(request,
                report_options=RedsReportOptions.ALL,
                is_reds=True,
                filename='reds123_all.csv'):
    return csv_stream(reds_123_calc(report_options, is_reds), filename)


@login_required
def reds_report_uom(request):
    return reds_report(request, RedsReportOptions.MELBOURNE,
                       filename='reds123_uom.csv')


@login_required
def reds_report_all(request):
    return reds_report(request, is_reds=False, filename='reds_all.csv')


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
    context = report_for_code_ingest(ForCodeReportOptions.MELBOURNE)
    return render(request, 'for_percent_report.html', context)


@login_required
def for_code_ingest_all(request):
    context = report_for_code_ingest(ForCodeReportOptions.ALL)
    return render(request, 'for_percent_report.html', context)
