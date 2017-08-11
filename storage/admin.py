# Register your models here.
from django.contrib import admin

from .models import Allocation, CollectionProfile, Custodian, Domain, Ingest, \
    Request, Project, StorageProduct, Suborganization, Contact, Organisation, \
    IngestFile, LabelsAlias, Label, FieldOfResearch

admin.site.register(Allocation)
admin.site.register(CollectionProfile)
admin.site.register(Custodian)
admin.site.register(Domain)
admin.site.register(Ingest)
admin.site.register(Project)
admin.site.register(Request)
admin.site.register(StorageProduct)
admin.site.register(Suborganization)
admin.site.register(Contact)
admin.site.register(Organisation)
admin.site.register(IngestFile)
admin.site.register(LabelsAlias)
admin.site.register(Label)
admin.site.register(FieldOfResearch)
