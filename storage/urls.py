from django.conf.urls import url

from storage.views import ingests_for_week, collection_status, reds_report, \
    reds_report_uom, vicnode_funding_by_storage_product, \
    difference_between_reported_and_approved, ingests_over_time, \
    demographics_stream, unfunded_report, for_code_ingest_uom, \
    for_code_ingest_all, collection_detail, application_detail, contact_detail, \
    collection_index

urlpatterns = [
    url(r'^report/$', ingests_for_week),
    url(r'^report/(?P<days>[0-9]+)/$', ingests_for_week),
    url(r'^collection_status$', collection_status),
    url(r'^reds_report/$', reds_report),
    url(r'^reds_report_uom/$', reds_report_uom),
    url(r'^vicnode_funding_by_sp', vicnode_funding_by_storage_product),
    url(r'^diff_reported_and_approved/$',
        difference_between_reported_and_approved),
    url(r'^diff_reported_and_approved/(?P<target>[^/]+)$',
        difference_between_reported_and_approved),
    url(r'^total_ingest_over_time/$', ingests_over_time),
    url(r'^demographics/$', demographics_stream),
    url(r'^vicnode_unfunded/$', unfunded_report),
    url(r'^for_code_ingest_uom/$', for_code_ingest_uom),
    url(r'^for_code_ingest_all/$', for_code_ingest_all),
    url(r'^collections/$', collection_index, name='index'),
    url(r'^collection/(?P<collection_id>\d+)/$', collection_detail,
        name='detail'),
    url(r'^application/(?P<application_code>[a-zA-Z0-9_.-]+)$',
        application_detail, name='application_detail'),
    url(r'^contact/(?P<contact_id>\d+)/$', contact_detail,
        name='contact_detail'),

]
