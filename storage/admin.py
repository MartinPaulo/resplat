# Register your models here.
from django.contrib import admin
from django.db.models import TextField
from django.forms import ModelForm, TextInput, Textarea
from django.urls import reverse
from django.utils.html import format_html

from .models import Allocation, CollectionProfile, Custodian, Ingest, \
    Request, Collection, StorageProduct, Suborganization, Contact, \
    Organisation, IngestFile, LabelsAlias, Label, FieldOfResearch, Domain


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


class ContactAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['first_name', 'last_name', 'orcid', 'organisation',
                           'title', 'position']}),
        ('Business Contact Information', {'fields': ['business_phone_number',
                                                     'business_email_address']}),
        ('Personal Contact Information', {'fields': [
            'phone_number', 'mobile_number', 'email_address']}),
    ]
    list_display = ('full_name', 'organisation', 'position')
    list_filter = ['organisation', 'position']
    ordering = ['last_name', 'first_name']
    search_fields = ['first_name', 'last_name']


class FieldOfResearchAdmin(admin.ModelAdmin):
    fields = ('code', 'description')
    list_display = ('code', 'description')
    ordering = ['code']


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
    list_filter = ['collection', 'storage_product', 'extraction_date']
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
    list_filter = ['group']
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


class CustodianInline(admin.TabularInline):
    model = Custodian
    classes = ('collapse',)
    extra = 1
    fields = ('person', 'role')


class DomainInline(admin.TabularInline):
    model = Domain
    classes = ('collapse',)
    extra = 1
    fields = ('field_of_research', 'split')


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
    fieldsets = [
        (None, {'fields': [('name', 'collective'), 'status', 'rifcs_consent',
                           'overview', 'ingests_link']}),
    ]
    readonly_fields = ['ingests_link']
    inlines = [CustodianInline, ApplicationInline, DomainInline,
               CollectionProfileInline]
    list_display = ('name', 'status')
    list_display_links = ('name',)
    list_filter = ['status', 'collective']

    @admin_changelist_link(
        'ingests', 'Ingests',
        query_string=lambda c: 'collection__id__exact={}'.format(c.pk))
    def ingests_link(self, ingests):
        return 'For this collection'

    ordering = ['name']
    search_fields = ['name']
    form = CollectionAdminForm


class RequestAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['code', ('institution', 'faculty'),
                           'node', 'scheme', 'application_form',
                           'status', 'notes']}),
        ('Operation',
         {'fields': ['capital_funding_source', ], }),
    ]
    list_display = ('code', 'institution', 'scheme', 'status')
    list_filter = ['institution', 'scheme', 'status']
    search_fields = ['code']
    ordering = ['code']


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
