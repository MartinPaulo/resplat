import collections
import sys

from django.test import TestCase


class IngestTestCase(TestCase):
    fixtures = []

    # fixtures = ['test_fixtures/auths_fixtures.json'
    #     , 'test_fixtures/labels_fixtures.json'
    #     , 'test_fixtures/contacts_fixtures.json'
    #     , 'test_fixtures/changes_fixtures.json'
    #     , 'test_fixtures/applications_fixtures.json'
    #     , 'test_fixtures/ingest_fixtures.json'
    #     , 'test_fixtures/reports_fixtures.json'
    #     , 'test_fixtures/adhoc_fixtures.json']

    def check(self, parse_val, parse_err, check_val, check_err, field_name,
              line_num):
        self.assertEqual(parse_val, check_val,
                         field_name + ' value: Line ' + str(line_num))
        self.assertEqual(parse_err, check_err,
                         field_name + ' err: Line ' + str(line_num))


def print_error():
    error_type, value, traceback = sys.exc_info()
    print('######################## Error Exception ####################')
    print('type :' + error_type)
    print('value : ' + value)
    print('strerror: ' + value.strerror)
    print('#############################################################')


def print_map_sorted_by_key(coll):
    for k in collections.OrderedDict(sorted(coll.items())):
        print(k, coll.get(k))
