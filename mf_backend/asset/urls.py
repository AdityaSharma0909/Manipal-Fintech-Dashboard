from django.urls import path 
from .views.asset import AssetView,AssetDocumentView
from .views.GoldAppriasel import GoldAppriaselView
from .views.asset_document_id_view import DeleteAssetDocumentView
from .views.gold_prices import GoldPriceView
from .views.gold_prices_v2 import GoldPriceV2View
# from .views.manual_30_days_gold_data import ManualUploadGoldData

urlpatterns =[
    path('',AssetView.as_view()),
    path('documents/',AssetDocumentView.as_view()),
    path('appraisal/',GoldAppriaselView.as_view()),
    # path('manual_update', ManualUploadGoldData.as_view()),
    path('gold-price', GoldPriceView.as_view()),
    path('gold-price/v2', GoldPriceV2View.as_view()),
    path('delete_asset_document',DeleteAssetDocumentView.as_view())
]