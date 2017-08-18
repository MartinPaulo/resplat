from django.db import models
import datetime


class IngestFile(models.Model):
    """
    A record of the files giving usage ingested to date

    The fields removed from the VicNode table are:

    * completed

    """
    SOURCE_CHOICES = (('MON', 'Monash'), ('UOM', 'University of Melbourne'))
    SOURCE_LOCATIONS = ((1, 'Clayton'), (2, 'Queensbury'), (3, 'Noble Park'))
    TYPE_CHOICES = (('M', 'Market'), ('C', 'Computational'), ('V', 'Vault'),
                    ('X', 'Mixed'))
    id = models.AutoField(primary_key=True, help_text='the primary key')
    source = models.CharField(
        max_length=3, choices=SOURCE_CHOICES, null=False,
        db_column='file_source',
        help_text='the institution the file came from')
    location = models.SmallIntegerField(
        null=False, choices=SOURCE_LOCATIONS, db_column='file_location',
        help_text='the ???')
    type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, null=False, db_column='file_type',
        help_text='the storage product type covered by the file')
    extract_date = models.DateField(
        'Extract creation date', editable=False, blank=False, null=False,
        default=datetime.date.today,
        help_text='the date the file was processed')
    url = models.URLField(db_column='file_name',
        help_text='where the file was fetched from')

    def __str__(self):
        return f'{self.extract_date} {self.source} ' \
               f'{self.get_location_display()} {self.url}'

    class Meta:
        db_table = 'ingest_ingestfile'
        ordering = ['extract_date', 'location']
