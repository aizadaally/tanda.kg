from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart_item, name='update_cart_item'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
    path('count/', views.cart_count, name='cart_count'),
    path('clear/', views.clear_cart, name='clear_cart'),
]