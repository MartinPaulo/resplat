import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from storage.models.labels import GroupDefaultLabel


def validate_orcid(value):
    pattern = re.compile("http://orcid.org/\w{4}-\w{4}-\w{4}-\w{4}")
    if pattern.match(value):
        return
    raise ValidationError(
        'Required format: http://orcid.org/XXXX-XXXX-XXXX-XXXX, '
        'where X is [0-9,a-z,A-Z]')


class Contact(models.Model):
    """
    Collection contacts.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * updated_by_id
    * last_modified
    * active_flag
    * show_personal_contact_details
    * show_mobile_number
    * show_business_contact_details
    * notes

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    first_name = models.CharField(
        'First name of contact', max_length=30,
        help_text='first name of contact')
    last_name = models.CharField(
        'Last name of contact', max_length=30,
        help_text='last name of contact')
    phone_number = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='the contacts home phone number')
    mobile_number = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='the contacts mobile number')
    email_address = models.CharField(
        max_length=75, blank=True, null=True,
        help_text='the contacts home email address')
    business_phone_number = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='the contacts business phone number')
    business_email_address = models.CharField(
        max_length=75, blank=True, null=True,
        help_text='the contacts work email address')
    orcid = models.URLField(
        blank=True, null=True, verbose_name='ORCID of contact',
        validators=[validate_orcid],
        help_text='the contacts ORCID (if any)')
    organisation = models.ForeignKey(
        'storage.Organisation', models.DO_NOTHING, blank=True, null=True,
        related_name='contact_organisation',
        help_text='the contacts primary organisation')
    position = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Position'),
        default=GroupDefaultLabel('Position'),
        verbose_name='Organisation Position', related_name='contact_position',
        help_text='the contacts position at that organisation')
    title = models.ForeignKey(
        'storage.Label', models.DO_NOTHING, blank=True, null=True,
        limit_choices_to=Q(group__value__exact='Title'),
        default=GroupDefaultLabel('Title'),
        verbose_name='Contact Title', related_name='contact_title',
        help_text='the contacts title')

    @property
    def full_name(self):
        """Returns the contacts' full name."""
        return " ".join(filter(None, [self.first_name, self.last_name]))

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'contacts_contact'


class Organisation(models.Model):
    """
    The organisation a contact or collection is associated with.

    The fields removed from the VicNode table are:

    * creation_date
    * created_by_id
    * last_modified
    * updated_by_id
    * active_flag
    * number_weekly_working_days
    * number_weekly_working_hours
    * operational_center
    * operational_staff_petabyte
    * operational_staff_role
    * salary_overhead
    * weeks_of_annual_holiday
    * weeks_of_public_holiday
    * weeks_of_sick_leave
    * year_end
    * year_start

    """
    id = models.AutoField(primary_key=True, help_text='the primary key')
    short_name = models.CharField(
        max_length=20, blank=True, null=True,
        help_text='the brief name for the organisation')
    name = models.ForeignKey(
        'storage.Label', models.DO_NOTHING,
        limit_choices_to=Q(group__value__exact='Organisation'),
        default=GroupDefaultLabel('Organisation'),
        related_name='organisation_name',
        help_text='the full name for the organisation')
    rifcs_email = models.EmailField(
        blank=True, null=True, verbose_name='Notification email address',
        help_text='the RIFCS contact email address for the organisation')
    ands_url = models.URLField(
        blank=True, null=True, verbose_name='ANDS url',
        help_text='the ANDS url for the organisation')

    def __str__(self):
        return self.name.value

    class Meta:
        db_table = 'contacts_organisation'
