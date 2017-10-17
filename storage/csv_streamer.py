__author__ = "https://docs.djangoproject.com/en/1.11/howto/outputting-csv/"

import csv

from django.http import StreamingHttpResponse


class Echo(object):
    """
    An object that implements just the write method of the file-like interface.
    """

    # noinspection PyMethodMayBeStatic
    def write(self, value):
        """
        Write the value by returning it, instead of storing in a buffer.
        :param value: what is to be written
        :return: the passed in value
        """
        return value


def csv_stream(rows, file_name):
    """
    A view that streams a large CSV file.
    :param rows: the rows to be written as lines to the file
    :param file_name: the name of the file to be used
    :return: A StreamingHttpResponse with the content set to the csv to be
             returned
    """
    writer = csv.writer(Echo())
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
    return response
