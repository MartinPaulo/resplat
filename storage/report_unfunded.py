from decimal import *
from operator import attrgetter

from storage.models import Collection
from storage.report_funding import ReportRow, FundingReportRow, \
    FundingReportForCollection, AbstractFundingReportBase


class Bunch(list):
    """
    http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
    """

    def __init__(self, *args, **kwds):
        super().__init__()
        self[:] = list(args)
        setattr(self, '__dict__', kwds)


class UnfundedReportRow(ReportRow):
    def __init__(self, collection, storage_product, unfundedValue):
        self.id = collection.id
        self.code = collection.application_code
        self.name = str(collection.name)
        self.product = str(storage_product)
        self.value = unfundedValue

    def add(self, another_unfunded_row):
        self.value = self.value + another_unfunded_row.value

    def is_total(self):
        return self.product == self.TOTAL_KEY[1]

    def __str__(self):
        return '(id/name/product/value) = (%s/%s/%s/%s)' % (
            self.id, self.name, self.product, self.value)


class UnfundedReportForAllCollections(AbstractFundingReportBase):
    GLOBAL_TOTAL_COLLECTION = Bunch(app_id=-1, id=-1,
                                    application_code=FundingReportRow.ALL_TEXT,
                                    name=FundingReportRow.TOTAL_KEY[1])

    def __init__(self):
        super().__init__()
        self.total = UnfundedReportRow(self.GLOBAL_TOTAL_COLLECTION,
                                       FundingReportRow.TOTAL_KEY[1],
                                       Decimal(0.0))
        self.reportType = self.BY_UNFUNDED_COLLECTION
        self.report = self.generate_report()
        self.process_done = True

    def generate_report(self):
        result = []
        for collection in Collection.objects.all().order_by('name'):
            funding_report = FundingReportForCollection(collection)
            for storage_product in funding_report.global_data_dict.keys():
                dict_ = funding_report.global_data_dict[storage_product]
                unfunded_storage_product = dict_[FundingReportRow.UNFUNDED_KEY]
                if unfunded_storage_product and \
                                unfunded_storage_product.ingested > 0:
                    new_row = UnfundedReportRow(
                        collection, storage_product,
                        unfunded_storage_product.ingested)
                    result.append(new_row)
                    self.total.add(new_row)

        # Sort rows highest to lowest value
        result = sorted(result, key=attrgetter('value'), reverse=True)
        result.append(self.total)
        return result
