from django.urls import path, include
#from django.views.decorators.cache import cache_page

from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    products_list,
    #orders_list,
    create_product,
    ProductDetailView,
    ProductListView,
    OrderListView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductsDataExportView,
    ProductViewSet,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register('products', ProductViewSet, basename='products')

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path('api/', include(routers.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductListView.as_view(), name="products_list"),
    path('products/export/', ProductsDataExportView.as_view(), name='products_export'),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:pk>/update", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/confirm-delete", ProductDeleteView.as_view(), name="product_delete"),
    path("products/create/", create_product, name="product_create"),
    path("orders/", OrderListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
]
