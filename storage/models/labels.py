from django.db import models
from django.db.models import Q


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
        'self', models.DO_NOTHING, blank=True, null=True, default=1,
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

    def __str__(self):
        return self.value

    @classmethod
    def get_default_label(cls, group_value):
        """
        Returns the id of the first label belonging to the group or None

        :param group_value: The value of the group label
        :return: the id of the first group label | None if the group doesn't exist

        .. code-block::
            # example use
            Label.get_default_label('City')
        """
        group_id = Label.get_group_code(group_value)
        if group_id:
            group_labels = Label.objects.filter(group=group_id)
            if group_labels and group_labels.count() > 0:
                return group_labels.order_by('sequence_number').first().id
        return None

    @classmethod
    def get_group_code(cls, group_value):
        """
        Returns the id of the passed in group (has group = 1) value.

        :param group_value: The value of the group label
        :return: the id of the group label | None if the group doesn't exist

        .. code-block::
            # example use
            Label.get_group_code('City')
        """
        try:
            return Label.objects.get(value__exact=group_value, group=1).id
        except (Label.DoesNotExist, Label.MultipleObjectsReturned) as e:
            return None

    @classmethod
    def get_group_choices(cls, group_value):
        """
        Returns the labels that belong to the group, excluding the group label
        itself.

        :param group_value: The value of the group label
        :return: labels in the group | None if the group doesn't exist
        """
        try:
            group_label = Label.objects.get(value__exact=group_value, group=1)
            return Label.objects.filter(group=group_label)
        except (Label.DoesNotExist, Label.MultipleObjectsReturned) as e:
            return None

    class Meta:
        db_table = 'labels_label'
        unique_together = ('value', 'group')
        indexes = [models.Index(fields=['group', 'value'])]
        ordering = ['id']
