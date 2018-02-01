import datetime

from django.db import models


class IngestFileManager(models.Manager):

    def create_ingest_file(self, url, type, source, location,
                           extract_date, completed=False):
        return IngestFile(url=url, type=type, source=source, location=location,
                          extract_date=extract_date, completed=completed)


class IngestFile(models.Model):
    """
    A record of the files giving usage ingested to date
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
        help_text='the data hall')
    type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, null=False, db_column='file_type',
        help_text='the storage product type covered by the file')
    extract_date = models.DateField(
        'Extract creation date', editable=False, blank=False, null=False,
        default=datetime.date.today,
        help_text='the date the file was processed')
    url = models.URLField(db_column='file_name',
                          help_text='where the file was fetched from')
    # following is not used...
    completed = models.BooleanField(default=False, null=False)

    objects = IngestFileManager()

    def __str__(self):
        return '{ed} {s} {ld} {url}'.format(
            ed=self.extract_date, s=self.source,
            ld=self.get_location_display(), url=self.url)

    class Meta:
        db_table = 'ingest_ingestfile'
        ordering = ['extract_date', 'location']
