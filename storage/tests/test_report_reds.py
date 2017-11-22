from django.test import TestCase

from storage.models import Collection

_TEST_NAME = 'test'


class CollectionTestCase(TestCase):
    """
    To run these tests first make a copy of the production database (named
    vicnode in the example below):

        CREATE DATABASE test_db TEMPLATE vicnode;

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
