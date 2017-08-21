# Register your models here.
from django.contrib import admin
from django.db.models import TextField
from django.forms import ModelForm, TextInput, Textarea
from django.urls import reverse
from django.utils.html import format_html

from .models import Allocation, CollectionProfile, Custodian, Ingest, \
    Request, Collection, StorageProduct, Suborganization, Contact, Organisation, \
    IngestFile, LabelsAlias, Label, FieldOfResearch, Domain


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


class CollectionProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['collection']}),
        ('Merit', {'fields': ['merit_justification', ]}),
        ('Size', {'fields': ['estimated_final_size', ]}),
    ]
    list_display = ('collection',)
    ordering = ['collection']
    search_fields = ['collection__name']


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


class ProjectAdminForm(ModelForm):
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


class IngestInline(admin.TabularInline):
    model = Ingest
    classes = ('collapse',)
    extra = 1
    fields = (
        'storage_product', 'extraction_date', 'ingest_link', 'used_capacity')

    def ingest_link(self, instance):
        if instance.pk:
            url = reverse('admin:storage_ingest_change',
                          args=(instance.pk,))
            return format_html(u'<a href="{}">Link</a>', url)
        return ''

    readonly_fields = ('ingest_link',)


class ApplnInline(admin.TabularInline):
    model = Allocation
    can_delete = False
    classes = ('collapse',)
    extra = 1
    fields = ('application', 'application_link')
    max_num = 0
    verbose_name_plural = 'Applications'

    def application_link(self, instance):
        if instance.application.id:
            url = reverse('admin:storage_request_change',
                          args=(instance.application_id,))
            return format_html(u'<a href="{}">Link</a>', url)
        return ''

    readonly_fields = ('application', 'application_link',)


class CollectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [('name', 'collective'), 'status', 'rifcs_consent',
                           'overview']}),
    ]
    # IngestInline can return a large amount of rows and hence be very slow
    inlines = [CustodianInline, ApplnInline, DomainInline, IngestInline, ]
    list_display = ('name', 'status')
    list_display_links = ('name',)
    list_filter = ['status', 'collective']
    ordering = ['name']
    search_fields = ['name']
    form = ProjectAdminForm


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
admin.site.register(CollectionProfile, CollectionProfileAdmin)
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
