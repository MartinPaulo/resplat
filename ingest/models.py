from datetime import datetime

from django.db import models
from django.db.models import Q

from storage.models import Label
from storage.models import StorageProduct


def _get_date_str(obj):
    date_obj = obj
    if isinstance(obj, datetime):
        date_obj = obj.date()
    return str(date_obj)


# class Alias(models.Model):
#     value = models.CharField(max_length=100,
#                              verbose_name='alias literal value')
#     label = models.ForeignKey('Label', related_name='aliased_label',
#                               verbose_name='aliased label')
#     source = models.ForeignKey('Label', related_name='alias_source',
#                                verbose_name='alias source',
#                                limit_choices_to=Q(
#                                    group__value__exact='Alias Source'),
#                                blank=True, null=True)
#
#     class Meta:
#         verbose_name_plural = "Alias"
#         unique_together = ('label', 'value')
#         index_together = ['label']
#
#     def __str__(self):
#         return self.value


class IngestFileRun(models.Model):
    parent = models.ForeignKey('storage.IngestFile', null=False,
                               related_name='ingest_runs')
    metadata = models.TextField(null=True)
    process_date = models.DateTimeField('Ingest run time stamp',
                                        auto_now_add=True, editable=False,
                                        blank=False, null=False)
    run_error = models.TextField(null=True)

    def __str__(self):
        return 'Run ' + str(self.id) + ': ' + self.parent.__str__()


class IngestFileData(models.Model):
    ingest_parent_run = models.ForeignKey('ingest.IngestFileRun', null=False,
                                          related_name='ingest_results')
    line_number = models.SmallIntegerField(null=False)
    line_text = models.TextField(null=False)
    error = models.TextField(null=True)


class IngestCollectionError(models.Model):
    product = models.ForeignKey(StorageProduct, related_name='ingest_errors',
                                null=True)
    collKey = models.TextField()
    spKey = models.TextField()
    ingestFileRun = models.ForeignKey('ingest.IngestFileRun', null=False,
                                      related_name='ingest_errors')

    @property
    def extract_date(self):
        return self.ingestFileRun.parent.extract_date

    def __str__(self):
        return self.collKey + ' / ' + self.spKey + ' / ' + _get_date_str(
            self.extract_date)
