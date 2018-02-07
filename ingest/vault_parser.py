from django.contrib.auth.models import User

from ingest.compute_parser import UOMComputeParser
from ingest.test_utils import IngestTestCase
from ingest.utils import get_collection_appl_id_map, get_product_dict, \
    parse_float, DataSizes


class UOMVaultParser(UOMComputeParser):
    def get_storage_product_key_for_parser(self, cols):
        return 'Vault.Melbourne.Object'

    def get_allocated_capacity_column_details(self):
        return 4, DataSizes.GIGABYTE.bit_conversion_factor_gig

    def get_used_capacity_column_details(self):
        return 5, DataSizes.GIGABYTE.bit_conversion_factor_gig


##########################################################
#  Automated Tests
##########################################################

class DummyParserWithoutSave(UOMVaultParser):
    def process_ingest_row_data(self, extracted_ingest):
        return False, 'No save done'


class ParseUOMVaultWithoutSaveTestCase(IngestTestCase):
    def setUp(self):
        self.testUser = User.objects.create_user('TestUser',
                                                 'test@vicnode.org.at')
        self.extractDate = '2014-12-19'
        self.parser = DummyParserWithoutSave(self.extractDate, self.testUser)
        self.collectionDict = get_collection_appl_id_map()
        self.productDict = get_product_dict()

    def testValidParse(self):
        lineStream = [
            'tenant, vicnode_id, tenant_id, vault_quota, '
            'vault_used, compute_quota, compute_used',
            'Monash_Forensic_Data, 2013R4.1, '
            '5df4e9199a914449a14f88d22b53e63b, 0.0, 0.0, 0.0, 0.0',
            'C4D_Renderfarm, 2014R9.05, 57fb4d3f73534337b94fe5bbb8d04849, '
            '0.0, 0.0, 100.0, 100.0',
            'Epoch_of_Reionization, 2014R5.1, '
            'a75f28a8621344f187d5ccecf171649f, 0.0, 0.0, 0.0, 0.0',
            'AURIN-workflow, 2013R1.1, ed15a17952044ee4b2a260af81daa3f5, '
            '465.661, 0.0, 4500.0, 4500.0',
            'nex_gen_seq, 2014R6.2, 51c417fd7c7b4d648f58684065789682, '
            '51200.0, 0.0, 3000.0, 3000.0',
            'Interferome, 2014R9.06, 96a85d08c50945f0b95c0691ab8c1094, 0.0, '
            '0.0, 100.0, 100.0',
            'VicRoads_open_data, 2014R14.5, 5efcf00a5431448586564b8341ba6a17, '
            '10240.0, 0.0, 200.0, 200.0',
            'st_vincents_research, 2013R4.8,'
            ' 029a670a61ad492fa23f5befbee52452, 1024.0, 0.0, 2000.0, 2000.0',
            'Unimelb_Peter_Mac_Research_Dropbox, 2014R10.4, '
            '2197d1825ab44e4dba3b70f0e5afe432, 0.0, 0.0, 3000.0, 3000.0',
            'ACFS, 2014R7.1, c2c73c84d8174a34a8794b7ab199eed1, '
            '0.0, 0.0, 100.0, 100.0',
            'BIOENG_N67, 2014R8.2, 0608c0d6dbfc4980b703f86f987bc81b, '
            '0.0, 0.0, 15360.0, 15360.0',
            'OzFlux_Data_Portal, 2014R5.2, 7a8085ba38d548249163a368f5772a9b, '
            '0.0, 0.0, 160.0, 160.0',
            'IMOS, 2013R1.4, c76b369565e843b28a4338491001d15b, '
            '0.0, 0.0, 0.0, 0.0',
            'Neuropsychiatry_Centre, 2014R7.3, '
            'de1a24c3ccc44cb6ab52c8f1d4728b2f, 9313.226, 14.208, 0.0, 0.0',
            'Human_and_Animal_Neuroimaging, 2013R2.2, '
            '7da1b4a8570b4c4f9bcfec1e5ef2271f, 0.0, 0.0, 0.0, 0.0',
            'Melbourne_Materials_and_Fabrication_Platform, 2013R4.6, '
            '98c702bf8e4d4f7ea8b71adef1b38844, 13969.839, 2197.727, 0.0, 0.0',
            'LTRAC-WebAndGitServer, 2013R4.5, '
            '0720b7ccb3c9492cad95afe15158a7b4, 0.0, 0.0, 10.0, 10.0',
            'The_Proteome_Browser, 2013R3.5, '
            '04b5bd9f20c0439b9b9f934ebd63a1db, 0.0, 0.0, 30.0, 30.0',
            '1kp_services, 2014R6.4, 6119cd97a3bd478d809845aeacc6ea12, '
            '0.0, 0.0, 0.0, 0.0',
            'Geodataserver, 2014R8.3, 09a278ca47724f958760634ea333e25b, '
            '0.0, 0.0, 20580.0, 20580.0',
            'RemoteLab_VeRSI, 2013R4.4, 8021e6d7ac9a4786b9db0a2e907495eb, '
            '0.0, 0.0, 0.0, 0.0',
            'Florey_Neuroscience_Collection, 2014R10.3, '
            '0437f08e793243de9ad938f55ec014c4, 29802.322, 0.0, 0.0, 0.0',
            'CO2CRC_Extranet, 2014R11.02, 2d64ad51a8d94ce29ef6e14adfb9e60a, '
            '0.0, 0.0, 50.0, 50.0',
            'Endo_VL, 2014R8.6, 2bb45090fdb74f8c81359fbe723e4ab5, '
            '0.0, 0.0, 20000.0, 20000.0',
            'Monash_Synchrotron_Storage_Service, 2013R2.1, '
            '3beca0e5a8534b4eba36b67389111fcc, 0.0, 0.0, 27000.0, 27000.0',
            'UoM_NGSDA, 2013R3.1, 4639f24700884a1cb49e6c38184df678, '
            '7168.0, 5294.207, 20480.0, 20480.0',
            'Melbourne_Femur_Collection, 2013R3.4, '
            '43204ef0170c49d3b9ad7dbf361f892d, 9313.226, 3435.506, 0.0, 0.0',
            'Genetic_Epidemiology_Lab_, 2014R13.1, '
            '5dd7f773ad4d469c874abec456259783, 102400.0, 10219.456, 0.0, 0.0'
        ]
        count = 0
        for line in lineStream:
            count += 1
            if count > 1:
                cols = line.split(',')
                parser = self.parser  # just to stop typing self.parser...
                parse_val, parse_err = parser.parse_extraction_date(cols)
                check_val, check_err = self.extractDate, None
                self.check(parse_val, parse_err, check_val, check_err,
                           'extractDate', count)
                parse_val, parse_err, col_num = parser.parse_collection_object(
                    cols)
                # get() will return None instead of keyError
                check_val = self.collectionDict.get(cols[1])
                if check_val:
                    self.check(parse_val, parse_err, check_val, None,
                               'collection', count)
                else:
                    check_err = 'Collection not found for ' + str(cols[1])
                    self.check(None, parse_err, None, check_err, 'collection',
                               count)
                parse_val, parse_err, col_num = \
                    parser.parse_storage_product_object(cols)
                prodKey = 'Vault.Melbourne'
                check_val = self.productDict.get(prodKey)
                if check_val:
                    self.check(parse_val, parse_err, check_val, None,
                               'storage product', count)
                else:
                    check_err = 'StorageProduct not found for ' + prodKey
                    self.check(parse_val, parse_err, None, check_err,
                               'storage product', count)
                parse_val, parse_err = \
                    parser.parse_allocated_capacity_in_gb(cols)
                check_val, check_err = parse_float(cols[3])
                check_val *= 1000
                if parse_err and parse_err.startswith('internal'):
                    check_err = 'internal error: ' \
                                'allocated capacity column not defined'
                self.check(parse_val, parse_err, check_val, check_err,
                           'allocated capacity', count)
                parse_val, parse_err = parser.parse_used_capacity_in_gb(cols)
                check_val, check_err = parse_float(cols[4])
                check_val *= 1000
                if parse_err and parse_err.startswith('internal'):
                    check_err = 'internal error: ' \
                                'used capacity column not defined'
                self.check(parse_val, parse_err, check_val, check_err,
                           'used capacity', count)
                parse_val, parse_err = parser.parse_used_replica_in_gb(cols)
                check_val, check_err = parse_float("0")
                check_val *= 1000
                self.check(parse_val, parse_err, check_val, check_err,
                           'used replica', count)
