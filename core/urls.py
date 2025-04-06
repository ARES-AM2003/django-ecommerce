from django.urls import path
from core import views
from payment import views as payment_views
import uuid

urlpatterns = [
    path("", views.index, name="index"),
    path("add_product", views.add_product, name="add_product"),
    path("product_desc/<pk>", views.product_desc, name="product_desc"),
    path("add_to_cart/<pk>", views.add_to_cart, name="add_to_cart"),
    path("orderlist", views.orderlist, name="orderlist"),
    path("add_item/<int:pk>", views.add_item, name="add_item"),
    path("remove_item/<int:pk>", views.remove_item, name="remove_item"),
    path("checkout_page", views.checkout_page, name="checkout_page"),
    path("payment", payment_views.payment, name="payment")
    ,

    path("manageProducts", views.manageProducts, name="mangeProducts"),
    path('delete_product/', views.delete_product, name='delete_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),
    path('update_products/', views.update_product_list, name='update_product_list'),
    path('update-product/<int:pk>/', views.update_product_form, name='update_product_form'),
    path('products/', views.all_products, name='all_products'),
    path("esewa/success/", views.esewa_success, name="esewa_success"),
    path("esewa/failure/", views.esewa_failure, name="esewa_failure"),
    path('products/all/', views.all_product, name='all_products'),
    path('products/all/<int:category_id>/', views.all_products_by_category, name='all_products_by_category'),
    path('esewa/payment/', payment_views.esewa_payment_process, name='esewa_payment_process'),
    path('invoice/<uuid:transaction_id>/', payment_views.invoiceById, name='invoice_by_id'),
]
