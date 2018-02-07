from abc import ABCMeta, abstractmethod

from ingest.abstract_base_vicnode_parser import AbstractBaseVicNodeParser


class AbstractBaseVicNodeUOMParser(AbstractBaseVicNodeParser):
    __metaclass__ = ABCMeta

    def __init__(self, extraction_date, user, coll_dict, prod_dict, col_size):
        self.processLine = False
        super(AbstractBaseVicNodeUOMParser, self).__init__(extraction_date,
                                                           user, coll_dict,
                                                           prod_dict, col_size)

    @abstractmethod
    def get_start_after_line(self):
        pass

    def get_end_line(self):
        return ''

    def get_collection_column_number(self):
        """
        :return colNum:
        """
        return 2

    def get_collection_key_for_parser(self, cols: list):
        collectionColumn = self.get_collection_column_number()
        return cols[collectionColumn - 1]

    def ignore_line(self, line_num: int, line: str):
        """
        :param line:
        :param line_num:
        :return: True if the line must not be processed
        """
        if self.processLine:
            if line.strip() == self.get_end_line():
                self.processLine = False
            else:
                return False, None
        elif line == self.get_start_after_line():
            self.processLine = True
        return True, None

    def get_allocated_capacity_column_details(self):
        pass  # ignored unless overridden, default implementation

    def get_used_capacity_column_details(self):
        pass  # ignored unless overridden, default implementation

##########################################################
#  Automated Tests
##########################################################
