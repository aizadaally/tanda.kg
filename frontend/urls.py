from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('producers/', views.producers, name='producers'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('producer/<int:pk>/', views.producer_detail, name='producer_detail'),
]