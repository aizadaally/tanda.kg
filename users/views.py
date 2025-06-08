# users/views.py - Complete working version

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .forms import SmartRegistrationForm, ProducerProfileForm
from .models import Producer, Favorite, toggle_favorite, is_favorite
from products.models import Product


@never_cache
@csrf_protect
def register(request):
    """Smart registration view with proper CSRF"""
    
    if request.method == 'POST':
        form = SmartRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Create user
                user = form.save()
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()
                
                # Create producer profile if needed
                if form.cleaned_data['account_type'] == 'producer':
                    Producer.objects.create(
                        user=user,
                        name=f"{user.first_name} {user.last_name}",
                        description="Новый производитель на Tanda.kg",
                        region='bishkek',
                        is_verified=False
                    )
                    messages.success(request, f'Аккаунт производителя создан! Войдите в систему.')
                else:
                    messages.success(request, 'Аккаунт покупателя создан! Войдите в систему.')
                
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Ошибка при создании аккаунта: {str(e)}')
        else:
            # Form has errors - they will be displayed in template
            pass
    else:
        form = SmartRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def become_producer(request):
    """Convert regular user to producer"""
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему, чтобы стать производителем')
        return redirect('login')
    
    # Check if user is already a producer
    if hasattr(request.user, 'producer'):
        messages.info(request, 'Вы уже являетесь производителем')
        return redirect('producer_dashboard')
    
    if request.method == 'POST':
        # Get form data
        business_name = request.POST.get('business_name')
        description = request.POST.get('description')
        region = request.POST.get('region')
        website = request.POST.get('website')
        
        if not all([business_name, description, region]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'users/become_producer.html')
        
        try:
            Producer.objects.create(
                user=request.user,
                name=business_name,
                description=description,
                region=region,
                website=website or '',
                is_verified=False  # Admin will verify
            )
            
            messages.success(request, 'Заявка на статус производителя отправлена! Ожидайте проверки администратора.')
            return redirect('producer_dashboard')
            
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return render(request, 'users/become_producer.html')
    
    # Show form
    regions = Producer.REGIONS
    return render(request, 'users/become_producer.html', {'regions': regions})


@login_required
def producer_dashboard(request):
    """Producer dashboard with orders and products"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    # Get producer's products
    try:
        from orders.models import Order
        
        products = Product.objects.filter(producer=producer).order_by('-created_at')
        total_products = products.count()
        total_sales = sum(product.num_sales for product in products)
        
        # Get orders for producer's products
        orders = Order.objects.filter(
            product__producer=producer
        ).select_related(
            'user', 'product'
        ).order_by('-created_at')
        
        # Orders statistics
        pending_orders = orders.filter(status='pending').count()
        paid_orders = orders.filter(status='paid').count()
        completed_orders = orders.filter(status='completed').count()
        total_revenue = orders.filter(
            status__in=['paid', 'completed']
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Recent orders (last 10)
        recent_orders = orders[:10]
        
    except Exception as e:
        print(f"Error in producer_dashboard: {e}")
        products = []
        orders = []
        recent_orders = []
        total_products = 0
        total_sales = 0
        pending_orders = 0
        paid_orders = 0
        completed_orders = 0
        total_revenue = 0
    
    context = {
        'producer': producer,
        'products': products,
        'orders': orders,
        'recent_orders': recent_orders,
        'total_products': total_products,
        'total_sales': total_sales,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'users/producer_dashboard.html', context)


@login_required
def producer_orders(request):
    """Dedicated page for producer to view all their orders"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    # Get orders for producer's products
    from orders.models import Order
    
    orders = Order.objects.filter(
        product__producer=producer
    ).select_related(
        'user', 'product'
    ).order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter and status_filter in ['pending', 'paid', 'completed', 'cancelled']:
        orders = orders.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(product__name__icontains=search_query) |
            Q(buyer_name__icontains=search_query) |
            Q(buyer_phone__icontains=search_query)
        )
    
    context = {
        'producer': producer,
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'users/producer_orders.html', context)


@login_required
@require_POST
def update_order_status_producer(request):
    """Producer can update order status"""
    try:
        producer = request.user.producer
    except:
        return JsonResponse({
            'success': False,
            'message': 'Вы не являетесь производителем'
        })
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        status = data.get('status')
        
        if not order_id or not status:
            return JsonResponse({
                'success': False,
                'message': 'Не все данные указаны'
            })
        
        from orders.models import Order
        order = Order.objects.get(
            id=order_id, 
            product__producer=producer
        )
        
        # Validate status transition
        valid_statuses = ['pending', 'paid', 'completed', 'cancelled']
        if status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'message': 'Неверный статус'
            })
        
        old_status = order.status
        order.status = status
        order.save()
        
        status_names = {
            'pending': 'Ожидает оплаты',
            'paid': 'Оплачен',
            'completed': 'Завершен',
            'cancelled': 'Отменен'
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Статус заказа №{order.id} изменен на "{status_names[status]}"',
            'new_status': status,
            'status_display': status_names[status]
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Заказ не найден или не принадлежит вам'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@login_required
def edit_producer_profile(request):
    """Edit producer profile"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    if request.method == 'POST':
        # Update producer info
        producer.name = request.POST.get('name', producer.name)
        producer.description = request.POST.get('description', producer.description)
        producer.region = request.POST.get('region', producer.region)
        producer.website = request.POST.get('website', producer.website)
        producer.phone_number = request.POST.get('phone_number', producer.phone_number)
        producer.whatsapp_number = request.POST.get('whatsapp_number', producer.whatsapp_number)
        
        # Handle file uploads
        if 'logo' in request.FILES:
            producer.logo = request.FILES['logo']
        if 'qr_code' in request.FILES:
            producer.qr_code = request.FILES['qr_code']
        
        producer.save()
        messages.success(request, 'Профиль обновлен!')
        return redirect('producer_dashboard')
    
    regions = Producer.REGIONS
    context = {
        'producer': producer,
        'regions': regions,
    }
    return render(request, 'users/edit_producer_profile.html', context)


# FAVORITES VIEWS
@login_required
def favorites_view(request):
    """Display user's favorite products"""
    favorites = Favorite.objects.filter(user=request.user).select_related('product', 'product__producer')
    favorite_products = [fav.product for fav in favorites]
    
    context = {
        'favorites': favorites,
        'favorite_products': favorite_products,
    }
    return render(request, 'users/favorites.html', context)


@login_required
@require_POST
def toggle_favorite_view(request):
    """AJAX endpoint to toggle product in favorites"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        check_only = data.get('check_only', False)
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if check_only:
            # Just check if it's favorite
            is_fav = is_favorite(request.user, product)
            return JsonResponse({
                'success': True,
                'is_favorite': is_fav
            })
        
        # Toggle favorite
        is_favorited = toggle_favorite(request.user, product)
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorited,
            'message': f'{product.name} {"добавлен в" if is_favorited else "удален из"} избранное'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@login_required
@require_POST 
def check_favorite_status(request):
    """Check if product is in user's favorites"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        is_fav = is_favorite(request.user, product)
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_fav
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


# Store location management stubs
@login_required
def add_store_location(request):
    return HttpResponse("Add store location page - Coming soon!")

@login_required
def edit_store_location(request, pk):
    return HttpResponse("Edit store location page - Coming soon!")

@login_required
def delete_store_location(request, pk):
    return HttpResponse("Delete store location - Coming soon!")