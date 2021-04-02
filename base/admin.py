from django.contrib import admin
from .models import Food, ConsumedFood
from import_export.admin import ImportExportModelAdmin
#Register your models here

@admin.register(Food)
class PersonAdmin(ImportExportModelAdmin):
    pass
admin.site.register(ConsumedFood)