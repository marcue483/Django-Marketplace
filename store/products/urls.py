from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('category/<slug:slug>/', views.category_detail, name='category-detail'),
    path('add/', views.product_create, name='product-create'),
    path('<int:pk>/', views.product_detail, name='product-detail'),
    path('my-products/', views.my_products, name='my-products'),
    path('<int:pk>/delete/', views.delete_product, name='delete-product'),
]
