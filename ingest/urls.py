from django.conf.urls import url

from ingest import file_parse

urlpatterns = [
    url(r'^(?P<fileSource>\w{3})/(?P<location>\d+)/(?P<fileType>\w{1})$',
        file_parse.ingest_file, name='ingest_file'),
]
