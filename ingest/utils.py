from datetime import datetime
from enum import unique, Enum

from storage.models import Label, StorageProduct, Collection


def get_product_dict():
    product_dict = {}
    group_label = Label.objects.get(value='Storage Product',
                                    group__value='Label')
    for prod_label in Label.objects.filter(group=group_label):
        try:
            product_dict[prod_label.value] = StorageProduct.objects.get(
                product_name=prod_label)
        except (StorageProduct.DoesNotExist,
                StorageProduct.MultipleObjectsReturned):
            pass  # Ignore, continue
    return product_dict


def get_collection_appl_id_map():
    return {c.application_code: c for c in Collection.objects.all()}


def parse_float(str_value):
    try:
        return float(str_value), None
    except ValueError:
        return None, 'Error parsing numeric value ' + str_value


def get_current_date():
    return datetime.now().date()


@unique
class DataSizes(Enum):
    # BYTE = 0
    # KILOBYTE = 10
    # MEGABYTE = 20
    GIGABYTE = 30
    TERABYTE = 40

    def gigabyte_conversion_factor(self):
        return 2 ** (self.value - DataSizes.GIGABYTE.value)

    def bit_conversion_factor_gig(self):
        return 10 ** (3 * (self.value - DataSizes.GIGABYTE.value) / 10)