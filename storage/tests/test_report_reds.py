from django.test import TestCase

from storage.models import Collection
from storage.report_reds import reds_123_calc, RedsReportOptions

import numpy as np
import pandas


_TEST_NAME = 'test'


class CollectionTestCase(TestCase):
    """
    To run these tests first make a copy of the production database (named
    vicnode in the example below):

        CREATE DATABASE test_db TEMPLATE vicnode;

    Then make sure the test database (named test_db in the example above) is
    referenced in the local_settings.py file (see the
    local_settings_template.py DATABASES dictionary for an example).
    Then run the tests giving instructions not to drop the database:

        ./manage.py test --keepdb
    """
    def setUp(self):
        Collection.objects.create(name=_TEST_NAME)

    def test_collection_fetch(self):
        c = Collection.objects.get(name=_TEST_NAME)
        self.assertEqual(c.name, _TEST_NAME)

    def tearDown(self):
        Collection.objects.get(name=_TEST_NAME).delete()



class Report_Reds_TestCase(TestCase):
    def setUp(self):
        # Read csv. The result is a numpy array of arrays
        data = pandas.read_csv('storage/tests/reds123_all.benchmark.csv').as_matrix()
        # Slice off the end beacuse we only campare the first 15 columns
        self.benchmark = data[:, 0:15]


    def test_all(self):
        # Generate report, removing header column
        raw = reds_123_calc(RedsReportOptions.ALL)[1:]
        # Convert to numpy array of arrays
        data_array = np.array(raw)
        # Slice off the end because we only compare the first 15 columns
        result = data_array[:, 0:15]

        # Compare
        equals = np.array_equal(self.benchmark, data_array)
        self.assertEqual(equals, True)


class Csv_TestCase(TestCase):
    def setUp(self):
        data = pandas.read_csv('storage/tests/123.csv').as_matrix()
        self.benchmark = data

    def test_basic(self):
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        data_array = np.array(data)

        equals = np.array_equal(self.benchmark, data_array)
        if equals == False:
            print(self.benchmark == data_array)

        self.assertEqual(equals, True)
