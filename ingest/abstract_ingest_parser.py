from abc import ABCMeta, abstractmethod
from datetime import timedelta

from django.contrib.auth.models import User

from ingest.file_parse import set_run_error
from ingest.parser_manager import get_dummy_ingest_file, get_next_ingest_run, \
    store_file_row
from ingest.test_utils import IngestTestCase
from ingest.utils import get_current_date
from storage.models import Ingest, Allocation, Label, Collection


def transpose_date(date_to_transpose, by_days):
    return date_to_transpose + timedelta(days=by_days)


def increase_date(date_to_increase, increase_by):
    return transpose_date(date_to_increase, increase_by)


def get_collection_status_list():
    retDict = {}
    for cs in Label.objects.filter(group__value='Collection Status').all():
        retDict[cs.value] = cs
    return retDict


class AbstractIngestParser(metaclass=ABCMeta):

    def __init__(self, extraction_date, user):
        self.user = user
        self.extraction_date = extraction_date
        self.tomorrow_date = increase_date(get_current_date(), 1)

        # Header data management
        self.required_headers = None
        self.header_line = None
        self.col_header_map = dict()
        self.header_error = False

        collection_status_map = get_collection_status_list()
        self.set_collection_status_on_ingest = True
        try:
            self.coll_status_alloc_approved = collection_status_map[
                'Allocation Approved']
            self.coll_status_provisioned = collection_status_map['Provisioned']
            self.coll_status_ingesting = collection_status_map['Ingesting']
        except:
            self.set_collection_status_on_ingest = False

    @abstractmethod
    def parse_collection_object(self, cols):
        """
        :param cols:
        :return: tuple (collectionObject, errorMessage,
                        collectionCodeForIngestRow)
        """
        return None, None, None

    @abstractmethod
    def parse_storage_product_object(self, cols):
        """
        :return: tuple (storageProductObject, errorMessage,
                        storageProductCodeForIngestRow)
        """
        return None, None, None

    @abstractmethod
    def parse_allocated_capacity_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (allocatedCapacity, errorMessage)
        """
        return None, None

    @abstractmethod
    def parse_used_capacity_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (usedCapacity, errorMessage)
        """
        return None, None

    @abstractmethod
    def parse_used_replica_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (usedCapacity, errorMessage)
        """
        return None, None

    def is_parse_valid(self):
        """
        :return: Boolean, Message
        """
        if self.extraction_date > self.tomorrow_date:
            return False, 'Extraction Date greater than tomorrow'
        return True, None

    @abstractmethod
    def ignore_line(self, line_num, line):
        """
        :param line_num:
        :param line:
        :return: True if the line must not be processed
        """
        return True

    @abstractmethod
    def process_ingest_row_data(self, extracted_ingest_row):
        """
        :param extracted_ingest_row:
        :return: tuple(success, errorMessage)
        """
        return None, None

    def get_col_splitter(self, line_num):
        """
        override get_col_splitter method to vary column splitter value for each
        line
        :param line_num:
        :return: tuple ((regex) string demarcating the columns in a given line
                         number, minimum columns expected when this splitter
                         is applied)
        """
        return ',', 1

    def process_header_line(self):
        if self.required_headers:
            err_list = []
            col_splitter, length = self.get_col_splitter(1)
            cols = self.header_line.split(col_splitter)
            for h in self.required_headers:
                try:
                    self.col_header_map[h] = cols.index(h)
                except:
                    err_list.append(h)
            if err_list:
                self.header_error = True
                err_msg = 'Missing header fields : ' + ', '.join(err_list)
                return False, err_msg
        return True, None

    def get_header_map_values_for_list(self, key_list):
        ret_list = []
        for k in key_list:
            val = self.col_header_map.get(k)
            if val:
                ret_list.append(val)
        return ret_list

    def get_new_ingest(self):
        row = Ingest()
        currentDate = get_current_date()
        row.creation_date = currentDate
        row.last_modified = currentDate
        row.active_flag = True
        if self.user:
            if self.user.is_authenticated():
                row.created_by = self.user
                row.updated_by = self.user
        return row

    def validate_ingest_is_allocated(self, collection, storage_product):
        return Allocation.objects.filter(
            collection=collection,
            storage_product=storage_product).count() > 0

    def parse_extraction_date(self, cols):
        """
        :param cols: tuple (extractionDate, errorMessage)
        :return:
        """
        if self.extraction_date:
            return self.extraction_date, None
        return None, 'Error: extraction date not available'

    def process_row_cols(self, curr_store_row, cols):
        """
        :param curr_store_row:
        :param cols:
        :return:
        """
        row = Ingest()
        row.extraction_date, error = self.parse_extraction_date(cols)
        if error:
            set_run_error(curr_store_row, error)
        elif row.extraction_date > self.tomorrow_date:
            set_run_error(curr_store_row,
                          'Row Ignored, Extraction Date greater than tomorrow')

        collection, error, rowCollCode = self.parse_collection_object(cols)
        if not collection:
            set_run_error(curr_store_row, error)
        else:
            row.collection = collection

        storage_product, error, code = self.parse_storage_product_object(cols)
        if not storage_product:
            set_run_error(curr_store_row, error)
        else:
            row.storage_product = storage_product

        if collection and storage_product:
            if not self.validate_ingest_is_allocated(collection,
                                                     storage_product):
                set_run_error(curr_store_row,
                              'Row Ignored, no allocation for ' +
                              collection.name + '/' +
                              storage_product.product_name.value)
                return False
        else:
            pass  # temporary...
            # collError = IngestCollectionError(
            #     ingestFileRun=currStoreRow.ingest_parent_run)
            # collError.collKey = rowCollCode
            # collError.spKey = sp_code
            # if storage_product:
            #     collError.product = storage_product
            #     collError.save()

        row.allocated_capacity, error = self.parse_allocated_capacity_in_gb(
            cols)
        if not row.allocated_capacity:
            set_run_error(curr_store_row, error)

        row.used_capacity, error = self.parse_used_capacity_in_gb(cols)
        if not row.used_capacity:
            set_run_error(curr_store_row, error)

        row.used_replica, error = self.parse_used_replica_in_gb(cols)
        if not row.used_replica:
            set_run_error(curr_store_row, error)

        if not curr_store_row.error:
            success, error_message = self.process_ingest_row_data(row)
            if success:
                if self.set_collection_status_on_ingest:
                    # update Collection status
                    try:
                        c = Collection.objects.get(pk=row.collection.id)
                        old_status = c.status
                        if c.status == self.coll_status_alloc_approved:
                            c.status = self.coll_status_provisioned
                        if row.used_capacity > 0:
                            if c.status == self.coll_status_provisioned:
                                c.status = self.coll_status_ingesting
                        if old_status != c.status:
                            c.save()
                    except (Collection.DoesNotExist,
                            Collection.MultipleObjectsReturned):
                        error_message = 'Collection Status error, ' \
                                        'collection id not found ' \
                                        '%s' % row.collection.id
                        # should not occur, as collection is guaranteed to be
                        # present at this stage
                        pass
                else:
                    error_message += ' Collection status could not be set. ' \
                                     'Collection status label error'

            if error_message:
                set_run_error(curr_store_row, error_message)
            elif not success:
                set_run_error(curr_store_row,
                              'Error processing extracted data')
            return success
        else:
            return False


##########################################################
#  Automated Tests
##########################################################
# from ingest.testUtils import IngestTestCase
# from django.contrib.auth.models import User

# from ingest.constants import ParserConstants
# from ingest.modelUtils import get_dummy_ingest_file, get_next_ingest_run, \
#     store_file_row


class DummyAbstractNegativeIngestParser(AbstractIngestParser):
    def parse_collection_object(self, cols):
        return None, 'Not implemented', 0

    def parse_storage_product_object(self, cols):
        return None, 'Not implemented', 0

    def parse_allocated_capacity_in_gb(self, cols):
        return None, 'Not implemented'

    def parse_used_capacity_in_gb(self, cols):
        return None, 'Not implemented'

    def parse_used_replica_in_gb(self, cols):
        return None, 'Not implemented'

    def ignore_line(self, line_num, line):
        return True

    def process_ingest_row_data(self, extracted_ingest_row):
        return False, 'Not Implemented'


class DummyAbstractPositiveIngestParser(AbstractIngestParser):
    def parse_collection_object(self, cols):
        return None, None, 0

    def parse_storage_product_object(self, cols):
        return None, None, 0

    def parse_allocated_capacity_in_gb(self, cols):
        return None, None

    def parse_used_capacity_in_gb(self, cols):
        return None, None

    def parse_used_replica_in_gb(self, cols):
        return None, None

    def ignore_line(self, line_num, line):
        return False

    def process_ingest_row_data(self, extracted_ingest_row):
        return True, None


class AbstractParserTestCase(IngestTestCase):
    def setUp(self):
        self.testUser = User.objects.create_user('TestUser',
                                                 'test@vicnode.org.at')
        self.negativeParser = DummyAbstractNegativeIngestParser(
            get_current_date(), self.testUser)
        self.positiveParser = DummyAbstractPositiveIngestParser(
            get_current_date(), self.testUser)
        self.ingestFile = get_dummy_ingest_file()
        self.ingestFileRun = get_next_ingest_run(self.ingestFile)

    def test_parse_row_cols(self):
        lineCount = 1
        data = '2014-12-19,MyTardis,MON-V1,250420,200189,MyTardis'.split(',')

        negativeStoreRow = store_file_row(lineCount, data, self.ingestFileRun)
        self.negativeParser.process_row_cols(negativeStoreRow, data)
        self.assertEqual(negativeStoreRow.error,
                         'Not implemented,Not implemented,Not implemented,'
                         'Not implemented,Not implemented,Not implemented, '
                         'Not implemented')
        lineCount += 1
        positiveStoreRow = store_file_row(lineCount, data, self.ingestFileRun)
        self.positiveParser.process_row_cols(positiveStoreRow, data)
        self.assertEqual(positiveStoreRow.error, None)
        if positiveStoreRow.error:
            print("Pos Error : " + positiveStoreRow.error)
