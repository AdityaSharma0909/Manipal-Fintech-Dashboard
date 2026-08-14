from django.contrib import admin
from asset.models import Asset, GoldPriceData, GoldAppriaselModel, GoldPriceHistory


# Register your models here.
class AssetAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Asset._meta.fields]


admin.site.register(Asset, AssetAdmin)


class GoldPriceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GoldPriceData._meta.fields]
    # list_editable = ['gold_price','karat', 'created_at']

admin.site.register(GoldPriceData, GoldPriceAdmin)


admin.site.register(GoldAppriaselModel)


class GoldPriceHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GoldPriceHistory._meta.fields]


admin.site.register(GoldPriceHistory, GoldPriceHistoryAdmin)
