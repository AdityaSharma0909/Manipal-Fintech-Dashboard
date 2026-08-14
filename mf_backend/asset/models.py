from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from branch.models import BranchUserMapping
from application.models import Application
from django.core.validators import MaxValueValidator, MinValueValidator
from lender.models import Lender
from django.db.models import UniqueConstraint
from utils.constants import GOLD_OWNERSHIP
from users.models import User

import uuid


class Asset(models.Model):
    asset_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    application=models.ForeignKey(Application,on_delete=models.CASCADE ,related_name="asset_application", null=True,blank=True)
    type=models.CharField(max_length=255)
    gross_weight=models.DecimalField(max_digits=15,decimal_places=2)
    karat_value=models.IntegerField()
    stone_weight=models.DecimalField(max_digits=15,decimal_places=2,blank=True,null=True)
    wastage=models.DecimalField(decimal_places=2,max_digits=20)
    net_weight=models.DecimalField(max_digits=15,decimal_places=2)
    net_weight_22k=models.DecimalField(max_digits=15,decimal_places=2,blank=True,null=True)
    leverage=models.IntegerField(blank=True,null=True)
    asset_price=models.DecimalField(decimal_places=2,max_digits=20,blank=True,null=True)
    rfdi_tag_number=models.CharField(max_length=255)
    gold_ownership=models.CharField(choices=[(e.value, e.value) for e in GOLD_OWNERSHIP],max_length=100,default=GOLD_OWNERSHIP.ancestral.value )
    asset_price_per_gram=models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    appriaser=models.ForeignKey(BranchUserMapping, blank=True, null=True ,on_delete=models.CASCADE)
    marketvalueatappraisal=models.DecimalField(decimal_places=2,max_digits=20)
    currentmarketvalue=models.DecimalField(decimal_places=2,max_digits=20)
    pouchnumber=models.CharField(max_length=50)
    

    def __str__(self) :
        return str(self.asset_id)
    

class GoldPriceData(models.Model):
    gold_price_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gold_price=models.DecimalField(decimal_places=2,max_digits=20)
    old_gold_price=models.DecimalField(decimal_places=2,max_digits=20, null=True, blank=True)
    karat=models.IntegerField(
        # unique=True,
        validators=[
            MaxValueValidator(22),
            MinValueValidator(18)
        ])
    # lending_price=models.PositiveIntegerField(default=0)
    lender = models.ForeignKey(Lender,on_delete=models.DO_NOTHING,related_name="lender_gold_price", null=True, blank=True)
    modified_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            # d = GoldPriceData.objects.filter(karat=self.karat).latest('-modified_at')
            d = GoldPriceData.objects.get(gold_price_id=self.gold_price_id)
            if d:
                self.old_gold_price = d.gold_price
            else:
                self.old_gold_price = self.gold_price
        except ObjectDoesNotExist:
            self.old_gold_price = self.gold_price
        # copy the other data you need here

        # the line below calls Model.save() which commits
        # your changes to the database
        super(GoldPriceData, self).save(*args, **kwargs)


    class Meta:
        constraints = [
            UniqueConstraint(fields=['karat', "lender"],name='lender_karat_unique'),
        ]

class GoldAppriaselModel(models.Model):
    goldappriase_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset=models.ForeignKey(Asset,on_delete=models.CASCADE)
    gross_weight=models.DecimalField(max_digits=15,decimal_places=2)
    karat_value=models.IntegerField()
    wastage=models.DecimalField(decimal_places=2,max_digits=20)
    net_weight=models.DecimalField(max_digits=15,decimal_places=2)
    # net_weight_22k=models.DecimalField(max_digits=15,decimal_places=2)
    pouch_no=models.CharField(max_length=255)
    eligible_amount=models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    asset_price=models.DecimalField(decimal_places=2,max_digits=20,blank=True,null=True)
    appriased_by=models.ForeignKey(User,on_delete=models.CASCADE)

    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)


class GoldPriceHistory(models.Model):
    gold_price_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gold_price=models.DecimalField(decimal_places=2,max_digits=20)
    lender = models.ForeignKey(Lender,on_delete=models.DO_NOTHING,related_name="lender_gold_price_history", null=True, blank=True)
    karat = models.IntegerField(
        validators=[
            MaxValueValidator(22),
            MinValueValidator(18)
        ])
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)