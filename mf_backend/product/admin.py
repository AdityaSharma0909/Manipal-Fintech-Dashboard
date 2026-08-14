from django.contrib import admin
from django import forms
# Register your models here.
from .models import Product,WhiteGoods,ProductSpecificDocuments, ProductWhiteGoodsMapping

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    # Optional: Add custom validation or cleanup for available_in_branches if necessary
    def clean_available_in_branches(self):
        branches = self.cleaned_data.get('available_in_branches')
        # Optionally, perform checks here (e.g., remove default branches if needed)
        return branches
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    filter_horizontal = ('available_in_branches',)
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Product._meta.fields]
    

admin.site.register(Product,ProductAdmin)

class WhiteGoodsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in WhiteGoods._meta.fields]
    

admin.site.register(WhiteGoods,WhiteGoodsAdmin)

class ProductSpecificDocumentsAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in ProductSpecificDocuments._meta.fields]
    

admin.site.register(ProductSpecificDocuments,ProductSpecificDocumentsAdmin)


class ProductWhiteGoodsMappingAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in ProductWhiteGoodsMapping._meta.fields] 

admin.site.register(ProductWhiteGoodsMapping,ProductWhiteGoodsMappingAdmin)


