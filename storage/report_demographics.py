from storage.models import Custodian, Collection

__author__ = 'mmohamed'


def _convert_to_report(report_obj_list):
    header_row = ['Name', 'Email', 'Operating Centre', 'Storage Product',
                  'Funding Source', 'Ingest Phase', 'Role',
                  'Supporting Institution']
    report_list = [header_row]
    for data_row in report_obj_list:
        if data_row.storage_product:
            row = [data_row.name, data_row.email, data_row.operating_centre,
                   data_row.storage_product, data_row.funding_source,
                   data_row.ingest_phase, data_row.role,
                   data_row.supporting_institution
                   ]
            report_list.append(row)
    return report_list


class DemographicsRow:
    MIXED = 'Mixed'

    def __init__(self):
        self.name = None
        self.email = None
        self.operating_centre = None
        self.storage_product = None
        self.funding_source = None
        self.ingest_phase = None
        self.role = None
        self.supporting_institution = None

    def cannot_benefit_from_new_custodian_role(self):
        return (self.role == self.MIXED) and \
               self.cannot_benefit_from_new_collection()

    # maybe improve performance by removing the operating_centre check?
    def cannot_benefit_from_new_collection(self):
        if self.storage_product == self.MIXED and \
                        self.funding_source == self.MIXED and \
                        self.ingest_phase == self.MIXED and \
                        self.operating_centre == self.MIXED:
            return True
        return False

    def fill_row_from_custodian(self, custodian):
        if not self.name:
            self.name = custodian.person.full_name
            self.supporting_institution = custodian.person.organisation.name.value
            self.email = custodian.person.email_address
            if not self.email:
                self.email = custodian.person.business_email_address
        if not self.role:
            self.role = custodian.role.value
        elif self.role != custodian.role.value:
            self.role = self.MIXED
        for collection in Collection.objects.filter(
                custodians__person=custodian.person).all():
            if self.cannot_benefit_from_new_collection():
                break
            self.fill_row_from_collection(collection)

    def fill_row_from_collection(self, collection):
        sp_alloc_dict = collection.get_allocations_by_storage_product()
        for storage_product in sp_alloc_dict:
            allocation_list, sp_alloc_size = sp_alloc_dict[storage_product]
            if sp_alloc_size > 0:
                if not self.storage_product:
                    self.storage_product = storage_product.product_name.value
                    self.operating_centre = storage_product.operational_center.value
                else:
                    if self.storage_product != storage_product.product_name.value:
                        self.storage_product = self.MIXED
                    if self.operating_centre != storage_product.operational_center.value:
                        self.operating_centre = self.MIXED
                for allocation in allocation_list:
                    scheme = allocation.application.scheme
                    if scheme:
                        if not self.funding_source:
                            self.funding_source = scheme.value
                        elif self.funding_source != scheme.value:
                            self.funding_source = self.MIXED
                if collection.status:
                    if not self.ingest_phase:
                        self.ingest_phase = collection.status.value
                    elif self.ingest_phase != collection.status.value:
                        self.ingest_phase = self.MIXED


def demographics_report():
    report_obj_list = []
    current_person = None
    for custodian in Custodian.objects.all().order_by('person'):
        if current_person == custodian.person:
            if current_row.cannot_benefit_from_new_custodian_role():
                continue
        else:
            current_row = DemographicsRow()
            report_obj_list.append(current_row)

        current_row.fill_row_from_custodian(custodian)
        current_person = custodian.person

    return _convert_to_report(report_obj_list)
