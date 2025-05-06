
from django.contrib import admin
from .models import *


admin.site.register(Brands)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_tag']
admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category','processor', 'brand','image_tag','status','is_featured']
    list_editable = ['status','is_featured']
admin.site.register(Products, ProductAdmin)

class RamAdmin(admin.ModelAdmin):
    list_display = ['ram']
admin.site.register(Ram, RamAdmin)

class StorageAdmin(admin.ModelAdmin):
    list_display = ['storage']
admin.site.register(Storage, StorageAdmin)

class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'ram','storage', 'price']

admin.site.register(ProductAttribute, ProductAttributeAdmin) 
