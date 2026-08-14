from django.urls import path
from .views.product import ProductView ,SingleProductView, ProductTestView
from .views.whitegoods import WhiteGoodsView, WhiteGoodsTestView
urlpatterns = [
    path("",ProductView.as_view()),
    path("goods/",WhiteGoodsView.as_view()),
    path("view/",SingleProductView.as_view()),
    path("add_all_products/",ProductTestView.as_view()),
    path("add_all_goods/",WhiteGoodsTestView.as_view()),
]
