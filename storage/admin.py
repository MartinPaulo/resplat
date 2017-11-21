# Register your models here.
import datetime
import json
import logging

from django.contrib import admin
from django.db.models import TextField, Q
from django.forms import ModelForm, TextInput, Textarea
from django.urls import reverse
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from storage.filters import RelatedDropDownFilter, FieldOfResearchFilter
from storage.models.applications import AccessLayer, AccessLayerMember
from .models import Allocation, CollectionProfile, Custodian, Ingest, \
    Request, Collection, StorageProduct, Suborganization, Contact, \
    Organisation, IngestFile, LabelsAlias, Label, FieldOfResearch, Domain

logger = logging.getLogger(__name__)


def admin_changelist_url(model):
    app_label = model._meta.app_label
    model_name = model.__name__.lower()
    return reverse('admin:{}_{}_changelist'.format(
        app_label,
        model_name)
    )


def admin_changelist_link(
        attr,
        short_description,
        empty_description="-",
        query_string=None
):
    """Decorator used for rendering a link to the list display of
    a related model in the admin detail page.

    attr (str):
        Name of the related field.
    short_description (str):
        Field display name.
    empty_description (str):
        Value to display if the related field is None.
    query_string (function):
        Optional callback for adding a query string to the link.
        Receives the object and should return a query string.

    The wrapped method receives the related object and
    should return the link text.

    Usage:
        @admin_changelist_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    See:
        https://medium.com/@hakibenita/things-you-must-know-about-django-admin-as-your-app-gets-bigger-6be0b0ee9614
    """

    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_changelist_url(related_obj.model)
            if query_string:
                url += '?' + query_string(obj)
            return format_html(
                '<a href="{}">{}</a>',
                url,
                func(self, related_obj)
            )

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


class AccessLayerAdmin(admin.ModelAdmin):
    fields = ('description', 'source')
    ordering = ['description']


class AllocationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['collection', 'application',
                           ('storage_product', 'size'),
                           ('operational_center', 'site'),
                           ('status',),
                           'notes']}),
        ('IDM Details', {'fields': [('idm_domain', 'idm_identifier')], }),
    ]
    list_display = ('application', 'collection', 'storage_product',
                    'size', 'operational_center')
    list_display_links = ('collection',)
    list_filter = ['status']
    ordering = ['collection__name']
    search_fields = ['collection__name', 'application__code']


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact


class ContactAdmin(ImportExportModelAdmin):
    fieldsets = [
        (None, {'fields': ['first_name', 'last_name', 'orcid', 'organisation',
                           'title', 'position']}),
        ('Business Contact Information', {'fields': ['business_phone_number',
                                                     'business_email_address']}),
        ('Personal Contact Information', {'fields': [
            'phone_number', 'mobile_number', 'email_address']}),
    ]
    list_display = ('full_name', 'organisation', 'position')
    list_filter = [('organisation', RelatedDropDownFilter),
                   ('position', RelatedDropDownFilter)]
    ordering = ['last_name', 'first_name']
    search_fields = ['first_name', 'last_name']
    resource_class = ContactResource


class FieldOfResearchAdmin(admin.ModelAdmin):
    fields = ('code', 'description')
    list_display = ('code', 'description')
    ordering = ['code']
    list_filter = (FieldOfResearchFilter,)
    readonly_fields = ('code', 'description',)
    actions = None

    def has_add_permission(self, request):
        # don't want user to add new ones...
        return False

    def has_delete_permission(self, request, obj=None):
        # or delete existing ones...
        return False

    def has_change_permission(self, request, obj=None):
        # or even see the complete list of FOR codes
        return False


class IngestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'extraction_date',
            ('collection', 'storage_product'),
            ('allocated_capacity', 'used_capacity', 'used_replica'),
            'ingested_raw_tb']}),
    ]
    list_display = ('storage_product', 'extraction_date', 'collection',
                    'allocated_capacity', 'used_capacity')
    list_display_links = ('storage_product', 'extraction_date', 'collection',)
    list_filter = [('collection', RelatedDropDownFilter),
                   ('storage_product', RelatedDropDownFilter),
                   'extraction_date']
    search_fields = ['collection__name']
    ordering = ['collection', 'storage_product', '-extraction_date']
    readonly_fields = ('ingested_raw_tb',)


class IngestFileAdmin(admin.ModelAdmin):
    fields = ['source', 'location', 'type', 'extract_date', 'url']
    list_display = ('source', 'location', 'type', 'extract_date', 'url')
    readonly_fields = ('extract_date',)


class AliasInline(admin.TabularInline):
    model = LabelsAlias
    fk_name = 'label'
    fields = ('value', 'source')
    extra = 1


class LabelAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['group', 'value', 'sequence_number']}),
        ('Parent Filter',
         {'fields': ['parent_type', 'parent'], 'classes': ['collapse']}),
        ('Application Flag',
         {'fields': ['application_flag'], 'classes': ['collapse']}),
    ]
    inlines = [AliasInline]
    list_display = ('group', 'sequence_number', 'value', 'parent')
    list_display_links = ('group', 'value')
    list_filter = [('group', RelatedDropDownFilter)]
    search_fields = ['value', 'aliased_label__value']
    ordering = ['group', 'sequence_number', 'value']


class ContactInline(admin.TabularInline):
    model = Contact
    classes = ('collapse',)
    extra = 1
    fields = ('first_name', 'last_name', 'title', 'position')


class OrganisationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': Textarea(
            attrs={'rows': 1,
                   'cols': 66,
                   'style': 'height: 1em;'})},
    }
    fieldsets = [
        (None, {'fields': [
            'name', 'short_name', ('rifcs_email', 'ands_url')]}),
    ]
    inlines = [ContactInline]
    list_display = ('name', 'short_name')
    ordering = ['name']


class CollectionAdminForm(ModelForm):
    class Meta:
        model = Collection
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': 80})
        }


class AccessLayerMemberInline(admin.TabularInline):
    model = AccessLayerMember
    classes = ('collapse',)
    extra = 1
    fields = ('accesslayer',)

    # We want to remove the ability add/change/delete the related fields...
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(AccessLayerMemberInline, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name in ('accesslayer',):
            field.widget.can_add_related = False
            field.widget.can_delete_related = False
        return field


class CustodianInline(admin.TabularInline):
    model = Custodian
    classes = ('collapse',)
    extra = 1
    fields = ('person', 'role')

    # We want to remove the ability add/change/delete the related fields...
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(CustodianInline, self).formfield_for_dbfield(db_field,
                                                                   **kwargs)
        if db_field.name in ('person', 'role'):
            field.widget.can_add_related = False
            field.widget.can_delete_related = False
        return field


class DomainInline(admin.TabularInline):
    model = Domain
    classes = ('collapse',)
    extra = 1
    fields = ('field_of_research', 'split')

    # We want to remove the ability add/change/delete the related fields...
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(DomainInline, self).formfield_for_dbfield(db_field,
                                                                **kwargs)
        if db_field.name in ('field_of_research', 'split'):
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        return field


class ApplicationInline(admin.TabularInline):
    model = Allocation
    can_delete = False
    classes = ('collapse',)
    extra = 1
    fields = ('application', 'application_link')
    max_num = 0
    verbose_name_plural = 'Applications'

    @staticmethod
    def application_link(instance):
        if instance.application.id:
            url = reverse('admin:storage_request_change',
                          args=(instance.application_id,))
            return format_html(u'<a href="{}">Link</a>', url)
        return ''

    readonly_fields = ('application', 'application_link',)


class CollectionProfileInline(admin.TabularInline):
    model = CollectionProfile
    classes = ('collapse',)
    extra = 1
    fields = ('merit_justification', 'estimated_final_size')
    max_num = 0
    verbose_name_plural = 'Collection profile'


class CollectionAdmin(admin.ModelAdmin):
    """
    https://medium.com/@hakibenita/how-to-turn-django-admin-into-a-lightweight-dashboard-a0e0bbf609ad

    =======
    Storage types
    == ====
    1  Computational.Melbourne
    3  Computational.Monash.Performance
    4  Market.Melbourne
    6  Market.Monash
    10 Vault.Melbourne.Object
    11 Vault.Monash
    14 Market.Monash.Object
    22 Market.Monash.File
    23  Market.Melbourne.Mediaflux
    24  Market.Melbourne.Gluster
    == ====

    """
    fieldsets = [
        (None, {'fields': [('name', 'collective'), 'status', 'rifcs_consent',
                           'link',
                           'overview', 'ingests_link']}),
    ]
    inlines = [CustodianInline, ApplicationInline, DomainInline,
               CollectionProfileInline, AccessLayerMemberInline]
    change_form_template = 'admin/collection.html'
    list_display = ('name', 'status')
    list_display_links = ('name',)
    list_filter = ['status', 'collective']
    ordering = ['name']
    readonly_fields = ['ingests_link']
    search_fields = ['name']

    @admin_changelist_link(
        'ingests', 'Ingests',
        query_string=lambda c: 'collection__id__exact={}'.format(c.pk))
    def ingests_link(self, ingest):
        num = Ingest.objects.filter(collection__id=ingest.instance.id).count()
        return '{} for this collection'.format(num)

    @staticmethod
    def make_date_handler():
        return lambda obj: (obj.isoformat() if isinstance(obj, (
            datetime.datetime, datetime.date)) else None)

    def changeform_view(self, request, object_id=None, form_url='',
                        extra_context=None):
        response = super().changeform_view(
            request, object_id=object_id, form_url=form_url,
            extra_context=extra_context)
        try:
            qs = response.context_data['original'].ingests.filter(
                Q(used_capacity__gt=0)).order_by('extraction_date')
            if qs.count():
                # can have multiple entries on the same date, as each storage
                # product used will have a separate value.
                # no need to gather used replica...
                ingests = [{'storage_product': x['storage_product_id'],
                            'extraction_date': x['extraction_date'],
                            'allocated_capacity': int(
                                x['allocated_capacity'] or 0),
                            'used_capacity': int(x['used_capacity'] or 0), }
                           for x in qs.values()]
                response.context_data['ingests_in_time_order'] = json.dumps(
                    ingests, default=self.make_date_handler())
        except (AttributeError, KeyError):
            logger.exception("Unexpected error on fetching ingests")
        return response


class AllocationInline(admin.TabularInline):
    model = Allocation
    extra = 1
    fields = (
        'storage_product', 'alloc_link', 'size', 'coll_link', 'collection')

    @staticmethod
    def coll_link(instance):
        if instance.pk:
            url = reverse('admin:storage_collection_change',
                          args=(instance.collection.pk,))
            return format_html(u'<a href="{}">Link</a>', url)
        return ''

    @staticmethod
    def alloc_link(instance):
        if instance.pk:
            url = reverse('admin:storage_allocation_change',
                          args=(instance.pk,))
            return format_html(u'<a href="{}">Link</a>', url)
        return ''

    readonly_fields = ('alloc_link', 'coll_link',)

    # We want to remove the ability add/change/delete the related fields...
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(AllocationInline, self).formfield_for_dbfield(db_field,
                                                                    **kwargs)
        if db_field.name in ('storage_product', 'collection'):
            field.widget.can_add_related = False
            field.widget.can_delete_related = False
        return field


class RequestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['code', ('institution', 'faculty'),
                           'node', 'scheme', 'application_form',
                           'status', 'notes']}),
        ('Operation',
         {'fields': ['capital_funding_source', ], 'classes': ['collapse']}),
    ]
    list_display = ('code', 'institution', 'scheme', 'status')
    list_filter = [('institution', RelatedDropDownFilter),
                   ('scheme', RelatedDropDownFilter), 'status']
    search_fields = ['code']
    ordering = ['code']
    inlines = [AllocationInline, ]


class StorageProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'operational_center', 'unit_cost',
                    'operational_cost', 'capacity')
    search_fields = ['product_name']
    ordering = ['product_name']


class SuborganizationAdminForm(ModelForm):
    class Meta:
        model = Collection
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': 80})
        }


class SuborganizationAdmin(admin.ModelAdmin):
    form = SuborganizationAdminForm


admin.site.register(AccessLayer, AccessLayerAdmin)
admin.site.register(Allocation, AllocationAdmin)
admin.site.register(Ingest, IngestAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(StorageProduct, StorageProductAdmin)
admin.site.register(Suborganization, SuborganizationAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(IngestFile, IngestFileAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(FieldOfResearch, FieldOfResearchAdmin)
