from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from . import views

# Custom logout view to handle both GET and POST
def logout_view(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    logout(request)
    return redirect('home')

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    # Custom logout that works with both GET and POST
    path('logout/', logout_view, name='logout'),
    
    path('register/', views.register, name='register'),
    
    # Producer management
    path('become-producer/', views.become_producer, name='become_producer'),
    path('dashboard/', login_required(views.producer_dashboard), name='producer_dashboard'),
    path('profile/edit/', login_required(views.edit_producer_profile), name='edit_producer_profile'),
    
    # Favorites
    path('favorites/', login_required(views.favorites_view), name='favorites_view'),
    path('favorites/toggle/', login_required(views.toggle_favorite_view), name='toggle_favorite'),
    path('check-favorite/', login_required(views.check_favorite_status), name='check_favorite_status'),
    
    # Store locations (stubs for now)
    path('store-location/add/', views.add_store_location, name='add_store_location'),
    path('store-location/<int:pk>/edit/', views.edit_store_location, name='edit_store_location'),
    path('store-location/<int:pk>/delete/', views.delete_store_location, name='delete_store_location'),
]