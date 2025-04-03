from django.contrib import admin
from . models import *

# Register your models here.
class VariantInline(admin.TabularInline):
    model = Variant


class VariantItemInline(admin.TabularInline):
    model = VariantItem


class CategoryAdmin(admin.ModelAdmin):
    list_display =['title', 'image']
    list_editable = ['image']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','price','regular_price']


