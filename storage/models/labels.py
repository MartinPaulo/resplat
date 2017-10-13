import logging

from django.db import models
from django.db.models import Q
from django.utils.deconstruct import deconstructible

logger = logging.getLogger(__name__)


# Todo: we can delete and remove this class
class LabelsAlias(models.Model):
    """
    Aliases for Labels

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * last_modified
    * updated_by_id
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    value = models.CharField(
        max_length=100, verbose_name='alias literal value',
        help_text='the value of the alias that will be shown')
    label = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        related_name='aliased_label', verbose_name='aliased label',
        help_text='the label that is aliased')
    source = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Alias Source'),
        related_name='alias_source', verbose_name='alias source',
        help_text='???')

    def __str__(self):
        return self.value

    class Meta:
        db_table = 'labels_alias'
        verbose_name = 'Label alias'
        verbose_name_plural = 'Label aliases'
        unique_together = ('label', 'value')
        indexes = [models.Index(fields=['label'])]


class LabelManager(models.Manager):
    def get_group_choices(self, group_value):
        """
        Returns the labels that belong to the group, excluding the group label
        itself.

        :param group_value: The value of the group label
        :return: labels in the group | None if the group doesn't exist
        """
        try:
            group_label = self.get(value__exact=group_value, group=1)
            return self.filter(group=group_label)
        except (Label.DoesNotExist, Label.MultipleObjectsReturned) as e:
            logger.warning("Group choice with value %s has a problem",
                           group_value, exc_info=1)
            return None

    def get_default_label(self, group_value):
        """
        Returns the id of the first label belonging to the group or None

        :param group_value: The value of the group label
        :return: the id of the first group label | None if the group doesn't
                 exist

        .. code-block::
            # example use
            Label.get_default_label('City')
        """
        group_id = self.get_group_code(group_value)
        if group_id:
            group_labels = self.filter(group=group_id)
            if group_labels and group_labels.count() > 0:
                return group_labels.order_by('sequence_number').first().id
        return None

    def get_group_code(self, group_value):
        """
        Returns the id of the passed in group (has group = 1) value.

        :param group_value: The value of the group label
        :return: the id of the group label | None if the group doesn't exist

        .. code-block::
            # example use
            Label.get_group_code('City')
        """
        try:
            return self.get(value__exact=group_value, group=1).id
        except (Label.DoesNotExist, Label.MultipleObjectsReturned) as e:
            logger.warning("Group code with value %s has a problem",
                           group_value, exc_info=1)
            return None


@deconstructible
class GroupDefaultLabel:
    """
    In order to look up a default label, if any, for a field, create an
    instance of this class using the group value as an argument to the
    constructor. Then, when django wants to populate the field it will call
    the class instance to get the desired value.

    So this is a callable, deconstructible class.

    Callable because we a way of making the instance respond to  django
    requesting the value.

    Deconstructible because we needed django migrations to be able to serialize
    instances of the class.

    Put another way: this class instance is the same as
    ``lambda: Label.objects.get_default_label('Group Value')``. The ``lambda``
    is required because django can't process the call whilst loading the
    database model. But django migrations can't serialize a ``lambda``. So this
    class presents the same construct in a serializable form.

    And yes, this class is a bit of a hack.

    See:

    * https://docs.djangoproject.com/en/1.11/topics/migrations/#migration-serializing
    * https://technobeans.com/2011/01/31/python-making-objects-callable/

    """

    def __init__(self, group_value):
        self.group_value = group_value

    def __call__(self):
        """
        :returns: the id of the first label belonging to the group or ``None``
        """
        return Label.objects.get_default_label(self.group_value)

    def __eq__(self, other):
        return self.group_value == other.group_value


class Label(models.Model):
    """
    A cunning trick to allow labels shown to the user to be edited.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * last_modified
    * updated_by_id
    * active_flag

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    value = models.CharField(
        max_length=250,
        help_text='the value that will be shown to the user')
    sequence_number = models.IntegerField(
        default=0,
        help_text='where this label is ordered in the group')
    application_flag = models.BooleanField(
        default=False,
        help_text='???')
    group = models.ForeignKey(
        'self', models.DO_NOTHING, blank=True, null=True,
        default=1,  # default to 'Label'
        limit_choices_to=Q(group__value__exact='Label'),
        related_name='Label_Group',
        help_text='the group this label belongs to')
    parent = models.ForeignKey(
        'self', models.DO_NOTHING, blank=True, null=True,
        related_name='Label_Parent',
        help_text='the parent label, if any')
    parent_type = models.ForeignKey(
        'self', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Label'),
        related_name='Label_Parent_Type',
        help_text='the type of the parent label, if any')

    objects = LabelManager()

    def __str__(self):
        return self.value

    class Meta:
        db_table = 'labels_label'
        unique_together = ('value', 'group')
        indexes = [models.Index(fields=['group', 'value'])]
        ordering = ['id']
