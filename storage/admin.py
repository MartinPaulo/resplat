# Register your models here.
from django.contrib import admin

from .models import Allocation
from .models import Project

admin.site.register(Allocation)
admin.site.register(Project)
