from django.contrib import admin
from .models import *
# Inline for Variants

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)



