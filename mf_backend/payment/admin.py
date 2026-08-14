from django.contrib import admin
from payment.models import Repayment, BharatSwasthyaRepayment, SalesOfficerPayout


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Repayment._meta.fields]


@admin.register(BharatSwasthyaRepayment)
class BharatSwasthyaRepaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BharatSwasthyaRepayment._meta.fields]


@admin.register(SalesOfficerPayout)
class SalesOfficerPayoutAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SalesOfficerPayout._meta.fields]
