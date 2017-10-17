from django.conf.urls import url

from storage.views import ingests_for_week, collection_status, reds_report, \
    reds_report_uom, vicnode_funding_by_storage_product

urlpatterns = [
    url(r'^report/$', ingests_for_week),
    url(r'^report/(?P<days>[0-9]+)/$', ingests_for_week),
    url(r'^collection_status$', collection_status),
    url(r'^reds_report', reds_report),
    url(r'^reds_report_uom', reds_report_uom),
    url(r'^vicnode_funding_by_sp', vicnode_funding_by_storage_product),

]
