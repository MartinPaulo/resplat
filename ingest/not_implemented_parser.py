from ingest.abstract_ingest_parser import AbstractIngestParser


class NotImplementedParser(AbstractIngestParser):
    def __init__(self, extraction_date, user):
        super(NotImplementedParser, self).__init__(extraction_date, user)

    def parse_collection_object(self, cols):
        """
        :param cols:
        :return: tuple (collectionObject, error_message)
        """
        return None, 'Not implemented'

    def parse_storage_product_object(self, cols):
        """
        :param cols:
        :return: tuple (storageProductObject, error_message)
        """
        return None, 'Not implemented'

    def parse_allocated_capacity_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (allocatedCapacity, error_message)
        """
        return None, 'Not implemented'

    def parse_used_capacity_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (usedCapacity, error_message)
        """
        return None, 'Not implemented'

    def parse_used_replica_in_gb(self, cols):
        """
        :param cols:
        :return: tuple (usedCapacity, error_message)
        """
        return None, 'Not implemented'

    def ignore_line(self, line_num, line):
        """
        :param line_num:
        :param line:
        :return: True if the line must not be processed
        """
        return True

    def process_ingest_row_data(self, extracted_ingest_row):
        """
        :param extracted_ingest_row:
        :return: tuple(success, error_message)
        """
        return False, 'Not Implemented'
