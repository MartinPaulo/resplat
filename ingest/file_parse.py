import json
import urllib.request
from datetime import datetime
from urllib.error import URLError

from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

from ingest.compute_parser import UOMComputeParser
from ingest.market_parser import UOMMarketParser
from ingest.models import IngestFileRun
from ingest.not_implemented_parser import NotImplementedParser
from ingest.parser_manager import IngestParserManager
from ingest.test_utils import IngestTestCase
from ingest.utils import get_current_date
from ingest.vault_parser import UOMVaultParser
from storage.models import IngestFile


def get_server_url(request):
    server = request.META['SERVER_NAME']
    port = request.META['SERVER_PORT']
    if port:
        server = server + ':' + str(port)
    return 'http://' + server


def get_error_dict(message):
    return {'success': False, 'message': message}


def get_success_dict(message):
    return {'success': True, 'message': message}


def as_json(result):
    if not result:
        result = get_error_dict('Empty result, Ingest failed')
    return HttpResponse(json.dumps(result), content_type='application/json')


def parse_date(value, date_format, field_name):
    try:
        return datetime.strptime(value, date_format).date(), None
    except ValueError as e:
        error = '%s / %s must be a valid date (format: %s) got %s'
        error %= (e, field_name, date_format, value)
        return None, as_json(get_error_dict(error))


def set_run_error(run_record, error):
    if not run_record:
        return  # TODO burying an unexpected state? At least log this
    if run_record.run_error:
        run_record.run_error = run_record.run_error + error
    else:
        run_record.run_error = error
    run_record.save()


def ingest_file(request, file_source, file_type, location):
    try:
        extract_date, error = parse_date(request.GET['extractDate'], '%Y%m%d',
                                         'extractDate')
        if error:
            return error
    except MultiValueDictKeyError:
        return as_json(get_error_dict('extractDate: multiple value error'))

    try:
        file_name = request.GET['fileName']
    except ValueError:
        return as_json(get_error_dict('fileName is a required parameter'))
    except MultiValueDictKeyError:
        return as_json(get_error_dict('fileName: multiple value error'))

    server_url = get_server_url(request)
    file_url = as_url(file_name, file_source, server_url)
    try:
        ingest_file_record = get_ingest_file(file_url, file_type,
                                             file_source,
                                             extract_date, location)
        if not ingest_file_record:
            return as_json(get_success_dict('File Ignored'))

        parser_manager = IngestParserManager()
        parser_list = get_parsers_for_request(extract_date, file_source,
                                              file_type,
                                              request.user)
        parser_errors = {}
        for p in parser_list:
            run_record = setup_ingest_file_run(ingest_file_record,
                                               request.META)
            parse_valid, error = p.is_parse_valid()
            if error:
                set_run_error(run_record, error)
                continue

            try:
                in_stream = []
                for word in urllib.request.urlopen(file_url).readlines():
                    in_stream.append(word.strip().decode('utf-8'))
                ingest_row_token_list, parser_errors[
                    p.__class__.__name__] = parser_manager.parse(in_stream,
                                                                 run_record, p)
            except URLError as e:
                set_run_error(run_record, str(e))
                parser_errors[p.__class__.__name__]['Error'] = str(e)

        ingest_file_record.completed = True
        for p in parser_errors:
            if len(p) > 0:
                ingest_file_record.completed = False
                break
        ingest_file_record.save()

        ret_dict = get_success_dict('File ingest completed. ')
        ret_dict['errors'] = parser_errors
        return as_json(ret_dict)
    except ValueError as e:
        return as_json(
            get_error_dict('ValueError:Parse Failed: ' + str(e)))
    except Exception as e:
        return as_json(
            get_error_dict('Exception:Parse Failed: ' + str(e)))


def get_ingest_file(url, file_type, source, extract_date,
                    location):
    """
    :param url:
    :param file_type:
    :param source:
    :param extract_date:
    :param location:
    :return: None if file processed earlier, else a new IngestFile record
    """
    try:
        row = IngestFile.objects.get(url=url,
                                     extract_date=extract_date,
                                     type=file_type,
                                     source=source)
        if row.completed:
            return None
    except IngestFile.DoesNotExist:
        row = IngestFile.objects.create_ingest_file(
            url=url,
            type=file_type,
            location=location,
            source=source,
            extract_date=extract_date)
        row.save()
    return row


def setup_ingest_file_run(ingest_file_record, metadata):
    runRecord = IngestFileRun()
    runRecord.parent = ingest_file_record
    runRecord.metadata = metadata
    runRecord.save()
    return runRecord


def as_url(file_name, file_source, server_url):
    result = server_url + '/static/market/'
    source = file_source.upper()
    if source == 'UOM':
        result = 'https://swift.rc.nectar.org.au/' \
                 'v1/AUTH_c84359b1de24472bab55ac28607feae4/vicnode_report/'
    elif source == 'MON':
        result = 'file:///mnt/sonasrpt/market/'
    else:
        pass  # TODO This is unexpected. Surely we should do something?
    return result + file_name


def get_parsers_for_request(extract_date, file_source, file_type, user):
    file_source_lower = file_source.lower()
    file_type_lower = file_type.lower()
    # we ignore 'mon' and 'mox'
    if file_source_lower == 'uom':
        if file_type_lower == 'm':
            return [UOMMarketParser(extract_date, user)]
        elif file_type_lower == 'c':
            return [UOMComputeParser(extract_date, user),
                    UOMVaultParser(extract_date, user)]
    return [NotImplementedParser(get_current_date(), user)]


##########################################################
#  Automated Tests
##########################################################


class ParseFileTestCase(IngestTestCase):

    def test_ignoreIngestFileMarkedAsComplete(self):
        """Files previously processed must be ignored"""
        url = 'http://localhost:8000/ingest/testFile'
        file_type = 'M'
        source = 'MON'
        extract_date = get_current_date()
        _ingest_file = IngestFile.objects.create_ingest_file(
            url=url, type=file_type, location=1, source=source,
            extract_date=extract_date, completed=True)
        _ingest_file.save()
        _ingest_file = get_ingest_file(url, file_type, source, extract_date, 1)
        self.assertEqual(_ingest_file, None)

    def test_newFileIngestStartup(self):
        """Files not processed earlier must be added to the system"""
        url = 'someMonashMarketFile'
        file_type = 'M'
        source = 'MON'
        location = 1
        extract_date = get_current_date()
        _ingest_file = get_ingest_file(url, file_type, source, extract_date,
                                       location)
        self.assertNotEqual(_ingest_file, None)
        ingest_file_run = setup_ingest_file_run(_ingest_file, '')
        self.assertNotEqual(ingest_file_run, None)
        self.assertEqual(ingest_file_run.parent.url, url)
        self.assertEqual(ingest_file_run.parent.type, file_type)
        self.assertEqual(ingest_file_run.parent.source, source)
        self.assertEqual(ingest_file_run.parent.extract_date, extract_date)
        self.assertEqual(ingest_file_run.parent.completed, False)
        try:
            ingestFileEntityRow = IngestFile.objects.get(
                url=url, extract_date=extract_date, type=file_type,
                source=source, location=location)
            self.assertEqual(ingestFileEntityRow, _ingest_file,
                             'Database record does not match row returned '
                             'by setStartProcess method')
            ingestRunEntityRow = IngestFileRun.objects.get(
                parent=ingestFileEntityRow)
            self.assertEqual(ingestRunEntityRow, ingest_file_run,
                             'Database record does not match row returned '
                             'by setup_ingest_file_run method')
        except IngestFile.DoesNotExist:
            self.assertEqual(1, 2, 'New file not added to IngestFile table')
