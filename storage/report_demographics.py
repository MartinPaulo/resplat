from storage.models import Custodian, Collection


class DemographicsRow:
    HEADERS = ['Name', 'Email', 'Operating Centre', 'Supporting Institution',
               'Collection ID', 'Storage Product', 'Funding Source', 'Role', ]

    SEPARATOR = ', '

    def __init__(self):
        self.name = None
        self.email = None
        self.operating_centre = None
        self.collection = None
        self.storage_product = None
        self.funding_source = None
        self.role = None
        self.supporting_institution = None

    def __str__(self):
        return f'{vars(self)}'

    def data(self):
        """
        :return: a list containing the values of the row, in the same order
                 as the HEADERS constant.
        """
        return [self.name, self.email, self.operating_centre,
                self.supporting_institution, self.collection,
                self.storage_product, self.funding_source, self.role,
                ]

    def fill_from_custodian(self, custodian):
        if not self.name:
            self.name = custodian.person.full_name
            self.supporting_institution = custodian.person.organisation.name.value
            self.email = custodian.person.email_address
            if not self.email:
                self.email = custodian.person.business_email_address
        if not self.role:
            self.role = custodian.role.value
        elif custodian.role.value not in self.role:
            self.role += self.SEPARATOR + custodian.role.value
        # for all collections that reference the custodian
        for collection in Collection.objects.filter(
                custodians__person=custodian.person).all():
            self._fill_from_collection(collection)

    def _fill_from_collection(self, collection):
        if not self.collection:
            self.collection = str(collection.id)
        elif str(collection.id) not in self.collection:
            self.collection += self.SEPARATOR + str(collection.id)
        sp_alloc_dict = collection.get_allocations_by_storage_product()
        for storage_product in sp_alloc_dict:
            allocation_list, sp_alloc_size = sp_alloc_dict[storage_product]
            if sp_alloc_size > 0:
                if not self.storage_product:
                    self.storage_product = storage_product.product_name.value
                    self.operating_centre = storage_product.operational_center.value
                else:
                    if storage_product.product_name.value not in self.storage_product:
                        self.storage_product += self.SEPARATOR + storage_product.product_name.value
                    if storage_product.operational_center.value not in self.operating_centre:
                        self.operating_centre += self.SEPARATOR + storage_product.operational_center.value
                for allocation in allocation_list:
                    scheme = allocation.application.scheme
                    if scheme:
                        if not self.funding_source:
                            self.funding_source = scheme.value
                        elif scheme.value not in self.funding_source:
                            self.funding_source += self.SEPARATOR + scheme.value


def _convert_to_list(rows):
    result = [DemographicsRow.HEADERS]
    for row in rows:
        if row.storage_product:
            result.append(row.data())
    return result


def demographics_report():
    """
    :return: for each contact, some basic information and also their associated
             collections, storage products, funding sources and roles
             (but only if they have an associated storage product)
    """
    report_rows = []
    last_custodian = None
    row = None
    for custodian in Custodian.objects.all().order_by('person'):
        if not row or last_custodian != custodian.person:
            # a new custodian gets a new row
            row = DemographicsRow()
            report_rows.append(row)
        row.fill_from_custodian(custodian)
        last_custodian = custodian.person
    return _convert_to_list(report_rows)
