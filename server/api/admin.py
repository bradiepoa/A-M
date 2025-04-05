from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


class VariantInLine(admin.TabularInline):
    model = Variant
    extra = 1  # Optional: how many blank forms to show

class ProductAdmin(admin.ModelAdmin):
    inlines = [VariantInLine]

admin.site.register(Product, ProductAdmin)
admin.site.register(Variant) 




