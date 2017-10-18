import sys
from abc import abstractmethod, ABC
from decimal import Decimal
from typing import Optional

from storage.models import Collection, Label


def _get_label_sequence_tuple(label) -> (Optional[int], str):
    """
    :param label: the label to be converted into a tuple
    :return: a tuple made of the labels sequence number and the label value
    """
    return label.sequence_number, label.value if label else None, 'Undefined'


def get_ordered_scheme_list():
    result = []
    for label in Label.objects.filter(
            group__value__exact='Allocation Scheme').order_by(
        'sequence_number').all():
        result.append(_get_label_sequence_tuple(label))
    return result


class ReportRow(ABC):
    UNFUNDED_KEY = (sys.maxsize - 1, 'Unfunded')
    TOTAL_KEY = (sys.maxsize, 'TOTAL')
    ALL_TEXT = 'ALL'


class FundingReportRow(ReportRow):
    def __init__(self):
        self.storage_product = None
        self.scheme = None
        self.data = None

    def is_unfunded(self):
        return (self.scheme == self.UNFUNDED_KEY[1]) or (
            self.storage_product == self.UNFUNDED_KEY[1])

    def is_total(self):
        return (self.scheme == self.TOTAL_KEY[1]) or (
            self.storage_product == self.TOTAL_KEY[1])


class FundingReportRowTuple:
    def __init__(self):
        self.awaiting = Decimal(0.0)
        self.approved = Decimal(0.0)
        self.ingested = Decimal(0.0)

    def __str__(self):
        return '(awaiting/approved/ingested) = ( ' + str(
            self.awaiting) + ',' + str(self.approved) + ',' + str(
            self.ingested) + ')'

    def update(self, allocation):
        status = str(allocation.application.status)
        if status in ('Submitted', 'Technically Assessed', 'Approved'):
            if allocation.size:
                if status == 'Approved':
                    self.approved = self.approved + allocation.size
                else:
                    self.awaiting = self.awaiting + allocation.size

    def add(self, other):
        self.awaiting = self.awaiting + other.awaiting
        self.approved = self.approved + other.approved
        self.ingested = self.ingested + other.ingested


class AbstractFundingReportBase(ABC):
    METRIC_GB = 'GB'
    METRIC_TB = 'TB'
    BY_STORAGE_PRODUCT = 'Storage Product'
    BY_ALLOCATION_SCHEME = 'Funding Programme'
    BY_UNFUNDED_COLLECTION = 'Unfunded Collection'

    def __init__(self):
        self.global_total = FundingReportRowTuple()
        self.global_data_dict = None
        self.process_done = False
        self.report = None
        self.type = None

    @abstractmethod
    def generate_report(self):
        pass

    def reset_global_data_dict(self):
        self.global_data_dict = {}

    def get_conversion_factor(self, metric):
        if metric == self.METRIC_TB:
            return Decimal(0.001)
        return Decimal(1.0)

    def print(self):
        for row in self.report:
            print(row)

    def generate_scheme_within_sp_report_rows(self):
        result = []
        for sp in sorted(self.global_data_dict.keys(), key=lambda x: str(x),
                         reverse=False):
            sp_obj = self.global_data_dict[sp]
            for scheme_tuple_key in sorted(sp_obj.keys(), key=lambda x: x[0],
                                           reverse=False):
                next_row = FundingReportRow()
                result.append(next_row)
                next_row.storage_product = str(sp)
                next_row.scheme = scheme_tuple_key[1]
                next_row.data = sp_obj[scheme_tuple_key]
        grand_total_row = FundingReportRow()
        grand_total_row.storage_product = FundingReportRow.ALL_TEXT
        grand_total_row.scheme = FundingReportRow.TOTAL_KEY[1]
        grand_total_row.data = self.global_total
        result.append(grand_total_row)
        return result


class FundingReportForCollection(AbstractFundingReportBase):
    def __init__(self, collection):
        super(FundingReportForCollection, self).__init__()
        self.collection = collection
        self.reportType = self.BY_STORAGE_PRODUCT
        self.report = self.generate_report()

    def get_allocations(self):
        if self.collection:
            return self.collection.allocations.all()
        else:
            raise Exception('Collection is required')

    def get_ingest_query(self, storage_product):
        qry = self.collection.ingests.filter(storage_product=storage_product)
        return qry.values('collection', 'extraction_date',
                          'used_capacity').order_by('collection',
                                                    '-extraction_date')

    def init_sp_scheme_data_dict(self, storage_product):
        result = {ReportRow.TOTAL_KEY: FundingReportRowTuple()}
        sp_ingest_query = self.get_ingest_query(storage_product)
        total_ingested_for_s_p = Decimal(0.0)
        if sp_ingest_query.count() > 0:
            coll_set = {}
            for row in sp_ingest_query:
                collection = row['collection']
                extraction_date = row['extraction_date']
                try:
                    if coll_set[collection] != extraction_date:
                        # multiple ingests can exist for the same extraction
                        # date
                        continue
                except KeyError:
                    coll_set[collection] = extraction_date
                used = row['used_capacity']
                if not used:
                    used = 0
                total_ingested_for_s_p = total_ingested_for_s_p + used
        unfunded = FundingReportRowTuple()
        unfunded.ingested = total_ingested_for_s_p
        result[ReportRow.UNFUNDED_KEY] = unfunded
        return result

    def collate_allocations(self):
        self.reset_global_data_dict()
        for alloc in self.get_allocations():
            sp = alloc.storage_product
            scheme_key_tuple = _get_label_sequence_tuple(
                alloc.application.scheme)
            try:
                sp_obj = self.global_data_dict[sp]
            except KeyError:
                sp_obj = self.init_sp_scheme_data_dict(sp)
                self.global_data_dict[sp] = sp_obj

            try:
                tuple_obj = sp_obj[scheme_key_tuple[0]]
            except KeyError:
                tuple_obj = FundingReportRowTuple()
                sp_obj[scheme_key_tuple] = tuple_obj

            tuple_obj.update(alloc)
        self.process_done = True

    def generate_report(self):
        self.summarize_report()
        return self.generate_scheme_within_sp_report_rows()

    def summarize_report(self):
        if not self.process_done:
            self.collate_allocations()

        for sp_obj in self.global_data_dict.keys():
            scheme_dict_for_sp_obj = self.global_data_dict[sp_obj]
            sp_unfunded = scheme_dict_for_sp_obj[FundingReportRow.UNFUNDED_KEY]
            sp_total = scheme_dict_for_sp_obj[FundingReportRow.TOTAL_KEY]

            for scheme in get_ordered_scheme_list():
                try:
                    sp_scheme_obj = scheme_dict_for_sp_obj[scheme]
                    if sp_unfunded.ingested > 0:
                        sp_scheme_obj.ingested = min(sp_unfunded.ingested,
                                                     sp_scheme_obj.approved)
                        sp_unfunded.ingested -= sp_scheme_obj.ingested
                    sp_total.add(sp_scheme_obj)
                except KeyError:
                    pass
            sp_total.add(sp_unfunded)
            self.global_total.add(sp_total)

    def print(self):
        for row in self.report:
            print(row.storage_product + '    ' + row.scheme + '    ' + str(
                row.data.awaiting) + '    ' + str(
                row.data.approved) + '    ' + str(row.data.ingested))


class FundingReportForAllCollectionsBySP(AbstractFundingReportBase):
    def __init__(self):
        super(FundingReportForAllCollectionsBySP, self).__init__()
        self.reportType = self.BY_STORAGE_PRODUCT
        self.report = self.generate_report()

    def generate_report(self):
        if not self.process_done:
            self.collate_collection_reports()
        return self.generate_scheme_within_sp_report_rows()

    def collate_collection_reports(self):
        self.reset_global_data_dict()
        for coll in Collection.objects.all():
            temp_report = FundingReportForCollection(coll)
            self.global_total.add(temp_report.global_total)
            for sp_obj in temp_report.global_data_dict.keys():
                temp_dict = temp_report.global_data_dict[sp_obj]
                try:
                    self_scheme_dict_for_sp_obj = self.global_data_dict[sp_obj]
                    for scheme_tuple_key in temp_dict.keys():
                        temp_data = temp_dict[scheme_tuple_key]
                        try:
                            self_scheme_data = self_scheme_dict_for_sp_obj[
                                scheme_tuple_key]
                            self_scheme_data.add(temp_data)
                        except KeyError:
                            self_scheme_dict_for_sp_obj[
                                scheme_tuple_key] = temp_data
                except KeyError:
                    self.global_data_dict[sp_obj] = temp_dict
        self.process_done = True
