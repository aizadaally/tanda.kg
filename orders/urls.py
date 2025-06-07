from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('success/', views.order_success, name='order_success'),
    path('mark-paid/', views.mark_order_paid, name='mark_order_paid'),
    path('update-status/', views.update_order_status, name='update_order_status'),
]