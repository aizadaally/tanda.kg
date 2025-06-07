from django.urls import path
from . import views

urlpatterns = [
    # Product management for producers
    path('add/', views.add_product, name='product_add'),
    path('<int:pk>/edit/', views.edit_product, name='product_edit'),
    path('<int:pk>/delete/', views.delete_product, name='product_delete'),
    
    # Reviews
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
    
    # AJAX endpoints
    path('ajax/mark-sold/<int:pk>/', views.mark_product_sold, name='mark_product_sold'),
]