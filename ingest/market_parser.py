from decimal import Decimal

from django.contrib.auth.models import User

from ingest.abstract_base_vic_node_uom_parser import \
    AbstractBaseVicNodeUOMParser
from ingest.test_utils import IngestTestCase
from ingest.utils import get_collection_appl_id_map, parse_float, \
    get_product_dict, DataSizes
from storage.models import Ingest


def append_ingest_row_data(extracted_ingest):
    if not isinstance(extracted_ingest, Ingest):
        return None, 'Expected Instance object, got ' + type(extracted_ingest)
    try:
        existing = Ingest.objects.get(
            extraction_date=extracted_ingest.extraction_date,
            collection=extracted_ingest.collection,
            storage_product=extracted_ingest.storage_product)
        existing.allocated_capacity = existing.allocated_capacity + Decimal(
            extracted_ingest.allocated_capacity)
        existing.used_capacity = existing.used_capacity + Decimal(
            extracted_ingest.used_capacity)
        existing.used_replica = existing.used_replica + Decimal(
            extracted_ingest.used_replica)
        try:
            existing.save()
            return True, 'Append successful'
        except Exception as e:
            return False, 'ingest row update fail: ' + str(e)
    except Ingest.DoesNotExist:
        try:
            extracted_ingest.save()
            return True, None
        except:
            return False, 'Error persisting data'


class UOMMarketParser(AbstractBaseVicNodeUOMParser):
    COL_SIZE = 8

    def __init__(self, extraction_date, user):
        super(UOMMarketParser, self).__init__(extraction_date, user,
                                              get_collection_appl_id_map(),
                                              get_product_dict(),
                                              self.COL_SIZE)

    def get_start_after_line(self):
        return 'tenant,vicnode_id,name,vserver,aggr,total,used,free'

    def get_storage_product_key_for_parser(self, cols):
        return 'Market.Melbourne'

    @classmethod
    def convert_tb_to_gb(cls, val_err):
        (val, err) = val_err
        if val:
            val *= DataSizes.TERABYTE.bit_conversion_factor_gig()
        return val, err

    def parse_allocated_capacity_in_gb(self, cols):
        allocColumn = 6
        return self.convert_tb_to_gb(parse_float(cols[allocColumn - 1]))

    def parse_used_capacity_in_gb(self, cols):
        repl_column = 3
        repl_string = "_repl"
        used_column = 7

        if cols[repl_column - 1].endswith(repl_string):
            return 0, None
        return self.convert_tb_to_gb(parse_float(cols[used_column - 1]))

    def parse_used_replica_in_gb(self, cols, **kwargs):
        repl_column = 3
        repl_string = "_repl"
        used_column = 7
        if cols[repl_column - 1].endswith(repl_string):
            return self.convert_tb_to_gb(parse_float(cols[used_column - 1]))
        return 0, None

    def process_ingest_row_data(self, extracted_ingest):
        return append_ingest_row_data(extracted_ingest)


##########################################################
#  Automated Tests
##########################################################


class DummyParserWithoutSave(UOMMarketParser):
    def process_ingest_row_data(self, extracted_ingest_row):
        return False, 'No save done'


class ParseUOMMarketWithoutSaveTestCase(IngestTestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('TestUser',
                                                  'test@vicnode.org.at')
        self.extract_date = '2014-12-19'
        self.parser = DummyParserWithoutSave(self.extract_date, self.test_user)
        self.collection_dict = get_collection_appl_id_map()
        self.product_dict = get_product_dict()

    def testValidParse(self):
        lineStream = [
            'tenant, vicnode_id, name, vserver, aggr, total, used, free',
            'Florey_Neuroscience_Collection, 2014R10.3, data01, '
            'os_0437f08e793243de9ad938f55ec014c4_01, '
            'aggr1_sata_04, 10.8, 0.0, 10.8',
            'CO2CRC_Extranet, 2014R11.02, data01_repl, '
            'os_2d64ad51a8d94ce29ef6e14adfb9e60a_01_repl, '
            'aggr1_sata_04, 2.7, 0.368, 2.332',
            'Genetic_Epidemiology_Lab_, 2014R13.1, data01, '
            'os_5dd7f773ad4d469c874abec456259783_01, '
            'aggr1_sata_04, 27.0, 0.0, 27.0',
            'VicNode_Test, Unknown, data01, '
            'os_7aaf95983f1f4d208f8b526ccbbfe36a_01, '
            'aggr2_sata_04, 0.9, 0.009, 0.891',
            'Human_and_Animal_Neuroimaging, 2013R2.2, data01, '
            'os_7da1b4a8570b4c4f9bcfec1e5ef2271f_01, '
            'aggr2_sata_04, 20.7, 3.664, 17.036',
            'nex_gen_seq, 2014R6.2, vaulttemp01, '
            'os_51c417fd7c7b4d648f58684065789682_01, '
            'aggr2_sata_02, 27.0, 8.595, 18.405',
            'Melbourne_Materials_and_Fabrication_Platform, 2013R4.6, data01, '
            'os_98c702bf8e4d4f7ea8b71adef1b38844_01, '
            'aggr1_sata_04, 0.9, 0.0, 0.9',
            'Unimelb_Peter_Mac_Research_Dropbox, 2014R10.4, data01, '
            'os_2197d1825ab44e4dba3b70f0e5afe432_01, '
            'aggr1_sata_04, 45.0, 0.253, 44.747',
            '1kp_services, 2014R6.4, data01_repl, '
            'os_6119cd97a3bd478d809845aeacc6ea12_01_repl, '
            'aggr1_sata_04, 9.0, 3.198, 5.802',
            'Melbourne_Femur_Collection, 2013R3.4, data01, '
            'os_43204ef0170c49d3b9ad7dbf361f892d_01, '
            'aggr1_sata_04, 9.0, 0.0, 9.0',
            'GRHANITE, Unknown, data01, '
            'os_a70aa8581d5740d3902319b3d54d40e2_01, '
            'aggr1_sata_04, 0.9, 0.0, 0.9',
            'Epoch_of_Reionization, 2014R5.1, data01, '
            'os_a75f28a8621344f187d5ccecf171649f_01, '
            'aggr2_sata_04, 4.5, 0.0, 4.5',
            'IMOS, 2013R1.4, data01, '
            'os_c76b369565e843b28a4338491001d15b_01, '
            'aggr1_sas_03, 5.4, 0.0, 5.4',
            'IMOS, 2013R1.4, data02, '
            'os_c76b369565e843b28a4338491001d15b_01, '
            'aggr1_sata_02, 27.0, 0.0, 14.26',
            'Neuropsychiatry_Centre, 2014R7.3, data01, '
            'os_de1a24c3ccc44cb6ab52c8f1d4728b2f_01, '
            'aggr1_sata_04, 10.8, 1.93, 8.87',
            'Neuropsychiatry_Centre, 2014R7.3, data01, '
            'os_de1a24c3ccc44cb6ab52c8f1d4728b2f_02, '
            'aggr1_sata_04, 2.7, 0.0, 2.7',
            'AURIN-workflow, 2013R1.1, data01, '
            'os_ed15a17952044ee4b2a260af81daa3f5_01, '
            'aggr1_sata_04, 13.5, 0.0, 13.5',
            'Florey_Neuroscience_Collection, 2014R10.3, data01_repl, '
            'os_0437f08e793243de9ad938f55ec014c4_01_repl, '
            'aggr1_sata_04, 10.8, 0.0, 10.8',
            'CO2CRC_Extranet, 2014R11.02, data01, '
            'os_2d64ad51a8d94ce29ef6e14adfb9e60a_01, '
            'aggr1_sata_04, 2.7, 0.368, 2.332',
            'Genetic_Epidemiology_Lab_, 2014R13.1, data01_repl, '
            'os_5dd7f773ad4d469c874abec456259783_01_repl, '
            'aggr1_sata_04, 27.0, 0.0, 27.0',
            'Human_and_Animal_Neuroimaging, 2013R2.2, data01, '
            'os_7da1b4a8570b4c4f9bcfec1e5ef2271f_01, '
            'aggr1_sata_04, 20.7, 3.754, 16.946',
            'Melbourne_Materials_and_Fabrication_Platform, 2013R4.6, '
            'data01_repl, '
            'os_98c702bf8e4d4f7ea8b71adef1b38844_01_repl, '
            'aggr1_sata_04, 0.9, 0.0, 0.9',
            'Unimelb_Peter_Mac_Research_Dropbox, 2014R10.4, data01_repl, '
            'os_2197d1825ab44e4dba3b70f0e5afe432_01_repl, '
            'aggr1_sata_04, 45.0, 0.255, 44.745',
            '1kp_services, 2014R6.4, data01, '
            'os_6119cd97a3bd478d809845aeacc6ea12_01, '
            'aggr1_sata_04, 9.0, 3.198, 5.802',
            'RemoteLab_VeRSI, 2013R4.4, data01, '
            'os_8021e6d7ac9a4786b9db0a2e907495eb_01, '
            'aggr2_sata_04, 9.0, 0.006, 8.994',
            'Melbourne_Femur_Collection, 2013R3.4, data01_repl, '
            'os_43204ef0170c49d3b9ad7dbf361f892d_01_repl, '
            'aggr1_sata_04, 9.0, 0.0, 9.0',
            'GRHANITE, Unknown, data01_repl, '
            'os_a70aa8581d5740d3902319b3d54d40e2_01_repl, '
            'aggr2_sata_02, 0.9, 0.0, 0.9',
            'Epoch_of_Reionization, 2014R5.1, data01, '
            'os_a75f28a8621344f187d5ccecf171649f_01, '
            'aggr2_sata_04, 4.5, 0.081, 4.419',
            'Neuropsychiatry_Centre, 2014R7.3, data01_repl, '
            'os_de1a24c3ccc44cb6ab52c8f1d4728b2f_01_repl, '
            'aggr1_sata_04, 10.8, 1.93, 8.87',
            'Neuropsychiatry_Centre, 2014R7.3, data01, '
            'os_de1a24c3ccc44cb6ab52c8f1d4728b2f_02, '
            'aggr1_sata_04, 2.7, 0.0, 2.7'
        ]
        count = 0
        for line in lineStream:
            count += 1
            if count > 1:
                cols = line.split(',')
                parseVal, parseErr = self.parser.parse_extraction_date(cols)
                checkVal, checkErr = self.extract_date, None
                self.check(parseVal, parseErr, checkVal, checkErr,
                           'extractDate', count)

                parseVal, parseErr, colNum = \
                    self.parser.parse_collection_object(cols)
                # get() will return None instead of keyError
                checkVal = self.collection_dict.get(cols[1])
                if checkVal:
                    self.check(parseVal, parseErr, checkVal, None,
                               'collection', count)
                else:
                    checkErr = 'Collection not found for ' + str(cols[1])
                    self.check(None, parseErr, None, checkErr, 'collection',
                               count)

                parseVal, parseErr, colNum = \
                    self.parser.parse_storage_product_object(cols)
                prodKey = 'Market.Melbourne'
                checkVal = self.product_dict.get(prodKey)
                if checkVal:
                    self.check(parseVal, parseErr, checkVal, None,
                               'storage product', count)
                else:
                    checkErr = 'StorageProduct not found for ' + prodKey
                    self.check(parseVal, parseErr, None, checkErr,
                               'storage product', count)

                checkVal, checkErr = parse_float(cols[6])
                checkVal *= 1000
                zeroVal, noneErr = parse_float("0")
                if cols[2].endswith('_repl'):
                    parseVal, parseErr = \
                        self.parser.parse_used_capacity_in_gb(cols)
                    self.check(parseVal, parseErr, zeroVal, noneErr,
                               'used capacity', count)
                    parseVal, parseErr = \
                        self.parser.parse_used_replica_in_gb(cols, )
                    self.check(parseVal, parseErr, checkVal, checkErr,
                               'used replica', count)
                else:
                    parseVal, parseErr = \
                        self.parser.parse_used_capacity_in_gb(cols)
                    self.check(parseVal, parseErr, checkVal, checkErr,
                               'used capacity', count)
                    parseVal, parseErr = \
                        self.parser.parse_used_replica_in_gb(cols, )
                    self.check(parseVal, parseErr, zeroVal, noneErr,
                               'used replica', count)
