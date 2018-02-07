from abc import ABCMeta, abstractmethod

from django.contrib.auth.models import User

from ingest.abstract_ingest_parser import AbstractIngestParser
from ingest.models import Alias
from ingest.test_utils import IngestTestCase
from ingest.utils import get_product_dict, DataSizes, get_current_date
from storage.models import Ingest, Label, Collection


class AbstractBaseVicNodeParser(AbstractIngestParser):
    __metaclass__ = ABCMeta

    def __init__(self, extraction_date, user, collection_dict, product_dict,
                 csv_split_col_size):
        self.product_dict = product_dict
        self.collection_dict = collection_dict
        self.csv_split_col_size = csv_split_col_size
        self.header_line = None
        super(AbstractBaseVicNodeParser, self).__init__(extraction_date, user)

    @abstractmethod
    def get_collection_key_for_parser(self, cols):
        pass

    def parse_collection_object(self, cols):
        """
        :return: tuple (collectionObject, errorMessage)
        """
        colValue = self.get_collection_key_for_parser(cols)
        if not colValue:
            return None, 'Collection not found for ', colValue

        if isinstance(colValue, str):
            colValue = colValue.strip()
        try:
            return self.collection_dict[colValue], None, colValue
        except:
            return None, 'Collection not found for ' + colValue, colValue

    @abstractmethod
    def get_storage_product_key_for_parser(self, cols):
        pass

    def parse_storage_product_object(self, cols):
        """
        :param cols: storage product col value
        :return: tuple (storageProductObject, errorMessage)
        """
        colValue = self.get_storage_product_key_for_parser(cols)
        if isinstance(colValue, str):
            colValue = colValue.strip()

        if not colValue:
            return None, 'StorageProduct not found for ', colValue

        try:
            return self.product_dict[colValue], None, colValue
        except:
            return None, 'StorageProduct not found for ' + colValue, colValue

    @abstractmethod
    def get_allocated_capacity_column_details(self):
        return 0, lambda x: x

    @staticmethod
    def _parse_float(str_value):
        try:
            return float(str_value), None
        except ValueError:
            return None, 'Error parsing numeric value ' + str_value

    def parse_allocated_capacity_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (allocatedCapacity, errorMessage)
        """
        alloc_col, data_size_fn = self.get_allocated_capacity_column_details()
        if alloc_col and alloc_col > 0:
            alloc_capacity, error = self._parse_float(cols[alloc_col - 1])
            if alloc_capacity:
                if alloc_capacity < 0:
                    alloc_capacity = float(0)
                else:
                    alloc_capacity *= data_size_fn()
            return alloc_capacity, error
        return None, 'internal error: allocated capacity column not defined'

    @abstractmethod
    def get_used_capacity_column_details(self):
        return 0, lambda x: x

    def parse_used_capacity_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (allocatedCapacity, errorMessage)
        """
        used_col_num, data_size_fn = self.get_used_capacity_column_details()
        if used_col_num and used_col_num > 0:
            used_capacity, err = self._parse_float(cols[used_col_num - 1])
            if used_capacity:
                used_capacity *= data_size_fn()
            return used_capacity, err
        return None, 'internal error: used capacity column not defined'

    def parse_used_replica_in_gb(
            self, cols,
            data_size_fn=DataSizes.GIGABYTE.gigabyte_conversion_factor):
        """
        :param cols:
        :param data_size_fn:
        :return: tuple (allocatedCapacity, errorMessage)
        """
        return 0, None

    def process_ingest_row_data(self, extracted_ingest):
        """
        :param extracted_ingest:
        :return: tuple(success, errorMessage)
        """
        if not isinstance(extracted_ingest, Ingest):
            return None, 'Expected Ingest instance, got ' + type(
                extracted_ingest)
        try:
            Ingest.objects.get(
                extraction_date=extracted_ingest.extraction_date,
                collection=extracted_ingest.collection,
                storage_product=extracted_ingest.storage_product)
            return False, 'ingest row fail: Data exists in DB'
        except Ingest.DoesNotExist:
            try:
                extracted_ingest.save()
                return True, None
            except Exception as e:
                return False, 'Error persisting data ' + str(e)

    def ignore_line(self, line_num, line):
        """
        :param line_num:
        :param line:
        :return: True if the line must not be processed
        """
        if line_num == 1:  # ignore Header line
            self.header_line = line
            header_ok, err_msg = self.process_header_line()
            if header_ok and not err_msg:
                err_msg = 'Row Ignored, Header Line'
            return True, err_msg

        if self.header_error:
            return True, 'Error in header line'

        return False, None

    def get_col_splitter(self, line_num):
        """
        override get_col_splitter method to vary column splitter value for each
        line
        :param line_num:
        :return: tuple ((regex) string demarcating the columns in a given line
                number, minimum columns expected when this splitter is applied)
        """
        return ',', self.csv_split_col_size


##########################################################
#  Automated Tests
##########################################################

class DummyBaseParser(AbstractBaseVicNodeParser):
    def get_collection_key_for_parser(self, cols):
        pass

    def get_storage_product_key_for_parser(self, cols):
        pass

    def get_allocated_capacity_column_details(self):
        pass

    def get_used_capacity_column_details(self):
        pass


def get_sonas_collection_dict():
    return get_collection_dict('Sonas Id')


def get_alias_records_for_group(group_label_value, alias_group_value):
    try:
        group_label = Label.objects.get(value=group_label_value,
                                        group__value='Label')
        alias_constant = Label.objects.get(value='Alias Source',
                                           group__value='Label')
        sonas_label_record = Label.objects.get(group=alias_constant,
                                               value=alias_group_value)
        return Alias.objects.filter(source=sonas_label_record,
                                    label__group=group_label)
    except (Alias.DoesNotExist, Alias.MultipleObjectsReturned,
            Label.DoesNotExist, Label.MultipleObjectsReturned):
        return None


def get_collection_dict(alias_group_value):
    sonas_collection_dict = {}
    for alias in get_alias_records_for_group('Collection Name',
                                             alias_group_value):
        try:
            sonas_collection_dict[alias.value] = Collection.objects.get(
                name=alias.label)
        except (Collection.DoesNotExist, Collection.MultipleObjectsReturned):
            pass  # Ignore, continue

    return sonas_collection_dict


class AbstractBaseVicNodeParserTestCase(IngestTestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('TestUser',
                                                  'test@vicnode.org.at')
        self.test_parser = DummyBaseParser(get_current_date(),
                                           self.test_user, {}, {}, 0)
        self.col_dict = get_sonas_collection_dict()
        self.prod_dict = get_product_dict()

    def getIngestForItem(self, item_num):
        ingest = self.test_parser.get_new_ingest()
        ingest.extraction_date = get_current_date()
        ingest.collection = list(self.col_dict.values())[item_num]
        ingest.storage_product = list(self.prod_dict.values())[item_num]
        ingest.allocated_capacity = 10
        ingest.used_capacity = 3
        ingest.used_replica = 1
        return ingest

    def test_shouldNotIngestExistingIngestAgain(self):
        ingest = self.getIngestForItem(0)
        ingest.save()
        success, errMsg = self.test_parser.process_ingest_row_data(ingest)
        self.assertEqual(success, False,
                         'Existing ingest record must not be updated')
        self.assertEqual(errMsg, 'ingest row fail: Data exists in DB',
                         'errorMsg incorrect for: '
                         'Existing ingest record must not be updated')

    def test_shouldIngestNewIngestAgain(self):
        newIngest = self.getIngestForItem(2)
        success, errMsg = self.test_parser.process_ingest_row_data(newIngest)
        self.assertEqual(success, True,
                         'New ingest record must be saved successfully, '
                         'got ' + str(success))
        self.assertEqual(errMsg, None,
                         'errorMsg must be None: '
                         'New ingest record must be saved successfully')

        try:
            checkIngestExists = Ingest.objects.get(
                extraction_date=newIngest.extraction_date,
                collection=newIngest.collection,
                storage_product=newIngest.storage_product)
            self.assertEqual(newIngest, checkIngestExists,
                             'DB Ingest does not match record sent to '
                             'process_ingest_row_data for save')
        except Ingest.DoesNotExist:
            self.assertEqual(True, False,
                             'Ingest saved using process_ingest_row_data does '
                             'not exist in DB')
