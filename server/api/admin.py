from django.contrib import admin
from . models import *

# Register your models here.
class VariantInline(admin.TabularInline):
    model = Variant


class VariantItemInline(admin.TabularInline):
    model = VariantItem



