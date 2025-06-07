from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import json

from cart.views import get_or_create_cart
from .models import Order


@login_required
@require_POST
def create_order(request):
    """Create order from cart items"""
    try:
        cart = get_or_create_cart(request)
        
        if not cart.items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Корзина пуста'
            })
        
        # Create orders for each cart item
        orders_created = []
        total_amount = 0
        
        for cart_item in cart.items.all():
            order = Order.objects.create(
                user=request.user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                total_price=cart_item.get_total_price(),
                buyer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                buyer_email=request.user.email,
                status='pending'
            )
            orders_created.append(order)
            total_amount += float(order.total_price)
        
        # Store order IDs in session for success page
        request.session['recent_order_ids'] = [order.id for order in orders_created]
        
        # Clear cart after creating orders
        cart.clear()
        
        return JsonResponse({
            'success': True,
            'message': f'Заказ оформлен! Создано {len(orders_created)} заказов на сумму {total_amount:.0f} сом.',
            'orders_count': len(orders_created),
            'total_amount': total_amount
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при создании заказа: {str(e)}'
        })


@login_required
def my_orders(request):
    """Display user's orders"""
    orders = Order.objects.filter(user=request.user).select_related(
        'product', 'product__producer'
    ).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'orders/my_orders.html', context)


def order_success(request):
    """Order success page with recent orders"""
    recent_orders = []
    
    # Get recent order IDs from session
    recent_order_ids = request.session.get('recent_order_ids', [])
    
    if recent_order_ids and request.user.is_authenticated:
        recent_orders = Order.objects.filter(
            id__in=recent_order_ids,
            user=request.user
        ).select_related('product', 'product__producer').order_by('-created_at')
        
        # Clear the session data
        request.session.pop('recent_order_ids', None)
    
    # If no recent orders, show last few orders from today
    if not recent_orders and request.user.is_authenticated:
        today = timezone.now().date()
        recent_orders = Order.objects.filter(
            user=request.user,
            created_at__date=today
        ).select_related('product', 'product__producer').order_by('-created_at')[:5]
    
    context = {
        'recent_orders': recent_orders
    }
    return render(request, 'orders/success.html', context)


@login_required
@require_POST
def mark_order_paid(request):
    """Mark order as paid"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            return JsonResponse({
                'success': False,
                'message': 'ID заказа не указан'
            })
        
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'paid'
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Заказ №{order.id} отмечен как оплаченный'
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Заказ не найден'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@login_required
@require_POST 
def update_order_status(request):
    """Update order status"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        status = data.get('status')
        
        if not order_id or not status:
            return JsonResponse({
                'success': False,
                'message': 'Не все данные указаны'
            })
        
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = status
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Статус заказа №{order.id} обновлен'
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Заказ не найден'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })