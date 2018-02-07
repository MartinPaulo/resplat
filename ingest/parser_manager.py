from datetime import datetime

from django.contrib.auth.models import User

from ingest.abstract_ingest_parser import DummyAbstractPositiveIngestParser
from ingest.models import IngestFileData, IngestFileRun
from ingest.test_utils import IngestTestCase
from storage.models import IngestFile


def record_error(data_record, error_msg):
    if data_record.error and error_msg:
        data_record.error = data_record.error + ', ' + error_msg
    elif error_msg:
        data_record.error = error_msg
    data_record.save()


def store_file_row(count, line_text, ingest_file_record):
    dataRecord = IngestFileData(ingest_parent_run=ingest_file_record)
    dataRecord.line_number = count
    dataRecord.line_text = line_text
    dataRecord.save()
    return dataRecord


def remove_line_feed_at_end(target):
    # and what about target.rstrip() ?
    k = len(target) - 2 if target.endswith("\r\n") else len(target)
    return target[:k]


class IngestParserManager:
    @staticmethod
    def tokenize_line(line, col_splitter, cols_expected, parser_name):
        cols = line.split(col_splitter)
        if not cols_expected or len(cols) < cols_expected:
            return cols, parser_name + ': expected a minimum of ' + str(
                cols_expected) + ' columns for splitter "' + str(
                col_splitter) + '" got ' + str(len(cols))
        return cols, None

    def parse(self, line_stream, ingest_file_run_record, parser):
        """
        :param parser:
        :param line_stream:
        :param ingest_file_run_record:
        :return:
        """
        count = 0
        input_stream_token_array = {}

        parse_error_list = []
        for line in line_stream:
            out_record = {'input': line}
            line = remove_line_feed_at_end(line)
            count += 1
            curr_store_row = store_file_row(count, line,
                                            ingest_file_run_record)
            if not parser:
                record_error(curr_store_row, 'No parser, row ignored')
                continue

            ignore, error_msg = parser.ignore_line(count, line)
            if error_msg:
                parse_error_list.append(
                    {'lineNum': count, 'input': line, 'error': error_msg})
            if ignore:
                error_msg = 'Row Ignored ' + (error_msg if error_msg else '')
                record_error(curr_store_row, error_msg)
                continue

            parser_name = parser.__class__.__name__
            col_splitter, expect_col_size = parser.get_col_splitter(count)
            cols, error_msg = self.tokenize_line(line, col_splitter,
                                                 expect_col_size, parser_name)
            if error_msg:
                record_error(curr_store_row, error_msg)
                parse_error_list.append(
                    {'lineNum': count, 'input': line, 'error': error_msg})
            else:
                out_record[col_splitter] = cols
                success = parser.process_row_cols(curr_store_row, cols)
                if not success:
                    parse_error_list.append({'lineNum': count, 'input': line,
                                             'error': curr_store_row.error})
            if curr_store_row.error:
                out_record['error'] = curr_store_row.error
            input_stream_token_array[count] = out_record
        return input_stream_token_array, parse_error_list


##########################################################
#  Automated Tests
##########################################################


def get_next_ingest_run(ingest_file):
    ingestFileRun = IngestFileRun(parent=ingest_file)
    ingestFileRun.save()
    return ingestFileRun


def get_dummy_ingest_file():
    url = 'http://localhost:8000/static/testFile'
    extract_date = datetime.now().date()
    return IngestFile.objects.create(url=url, type='M',
                                     source='MON', location=2,
                                     extract_date=extract_date)


class IngestParserManagerTestCase(IngestTestCase):
    def setUp(self):
        self.colSize = 5
        self.ingestManager = IngestParserManager()
        self.ingestFile = get_dummy_ingest_file()
        self.ingestFileRun = get_next_ingest_run(self.ingestFile)
        self.testUser = User.objects.create_user('TestUser',
                                                 'test@vicnode.org.at')
        self.parser = DummyAbstractPositiveIngestParser(datetime.now().date(),
                                                        self.testUser)

    def test_tokenize_line(self):
        line = 'sdasf,dfdsfd,5656,a34'
        cols, msg = self.ingestManager.tokenize_line(line, ',', self.colSize,
                                                     'Dummy')
        self.assertEqual(
            msg,
            'Dummy: expected a minimum of 5 columns for splitter "," got 4')

        line = 'sdasf,dfdsfd,5656,a34,tesss'
        cols, msg = self.ingestManager.tokenize_line(line, ',', self.colSize,
                                                     'Dummy')
        self.assertEqual(msg, None)
        self.assertEqual(len(cols), 5)

        line = 'dafdsf, 43e3d, sdasf,dfdsfd,5656,a34,tesss'
        cols, msg = self.ingestManager.tokenize_line(line, ',', self.colSize,
                                                     'Dummy')
        self.assertEqual(msg, None)
        self.assertEqual(len(cols), 7)

        line = 'dafdsf; 43e3d, sdasf; dfdsfd; 5656 ; a34:tesss'
        cols, msg = self.ingestManager.tokenize_line(line, ';', self.colSize,
                                                     'Dummy')
        self.assertEqual(msg, None)
        self.assertEqual(len(cols), 5)

    def test_parse(self):
        lines = ['sdasf,dfdsfd,5656,a34,tesss',
                 'dafdsf, 43e3d, sdasf,dfdsfd,5656,a34,tesss',
                 '1, 3,5,6,7,8',
                 'ad,eee,ttere,eterfer,4545t4gr,efe435'
                 ]
        # Test parse runs without exception
        parseResult, errCountMap = self.ingestManager.parse(lines,
                                                            self.ingestFileRun,
                                                            self.parser)
        # Check no lines were processed
        self.assertEqual(len(parseResult), 4)
        self.assertEqual(len(errCountMap), 0)
        # Check if all lines were persisted to storage
        savedLines = IngestFileData.objects.filter(
            ingest_parent_run=self.ingestFileRun)
        self.assertEqual(len(savedLines), len(lines))
