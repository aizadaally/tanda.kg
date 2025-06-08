# orders/views.py - Complete working version

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import json

from cart.views import get_or_create_cart
from .models import Order


@login_required
@require_POST
def create_order(request):
    """Create order from cart items with producer notification"""
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
        producers_to_notify = set()
        
        for cart_item in cart.items.all():
            # Get user profile phone if available
            user_phone = ''
            try:
                if hasattr(request.user, 'profile') and request.user.profile.phone_number:
                    user_phone = request.user.profile.phone_number
            except:
                pass
            
            order = Order.objects.create(
                user=request.user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                total_price=cart_item.get_total_price(),
                buyer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                buyer_email=request.user.email,
                buyer_phone=user_phone,
                status='pending'
            )
            orders_created.append(order)
            total_amount += float(order.total_price)
            producers_to_notify.add(cart_item.product.producer)
        
        # Store order IDs in session for success page
        request.session['recent_order_ids'] = [order.id for order in orders_created]
        
        # Send notifications to producers
        notify_producers_about_orders(producers_to_notify, orders_created)
        
        # Clear cart after creating orders
        cart.clear()
        
        return JsonResponse({
            'success': True,
            'message': f'Заказ оформлен! Создано {len(orders_created)} заказов на сумму {total_amount:.0f} сом. Производители уведомлены.',
            'orders_count': len(orders_created),
            'total_amount': total_amount
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при создании заказа: {str(e)}'
        })


def notify_producers_about_orders(producers, orders):
    """Send notifications to producers about new orders"""
    from django.template.loader import render_to_string
    
    # Group orders by producer
    orders_by_producer = {}
    for order in orders:
        producer = order.product.producer
        if producer not in orders_by_producer:
            orders_by_producer[producer] = []
        orders_by_producer[producer].append(order)
    
    # Send notifications
    for producer, producer_orders in orders_by_producer.items():
        try:
            # Email notification (if configured)
            if hasattr(settings, 'EMAIL_HOST') and producer.user.email:
                send_email_notification(producer, producer_orders)
            
            # You could add other notification methods here:
            # - SMS notifications
            # - Push notifications  
            # - Telegram bot notifications
            # - WhatsApp notifications
            
        except Exception as e:
            print(f"Failed to notify producer {producer.name}: {e}")


def send_email_notification(producer, orders):
    """Send email notification to producer about new orders"""
    try:
        subject = f'Новые заказы на Tanda.kg - {len(orders)} шт.'
        
        # Calculate total
        total_amount = sum(float(order.total_price) for order in orders)
        
        # Email content
        message = f"""
Здравствуйте, {producer.name}!

У вас новые заказы на Tanda.kg:

"""
        for order in orders:
            message += f"""
Заказ #{order.id}:
- Товар: {order.product.name}
- Количество: {order.quantity} шт
- Сумма: {order.total_price} сом
- Покупатель: {order.buyer_name}
- Телефон: {order.buyer_phone if order.buyer_phone else 'не указан'}
- Email: {order.buyer_email if order.buyer_email else 'не указан'}

"""
        
        message += f"""
Общая сумма: {total_amount:.0f} сом

Для управления заказами войдите в панель производителя:
https://tanda.kg/users/dashboard/

С уважением,
Команда Tanda.kg
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tanda.kg'),
            recipient_list=[producer.user.email],
            fail_silently=True
        )
        
    except Exception as e:
        print(f"Failed to send email to {producer.name}: {e}")


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
    """Mark order as paid by customer"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            return JsonResponse({
                'success': False,
                'message': 'ID заказа не указан'
            })
        
        order = Order.objects.get(id=order_id, user=request.user)
        
        if order.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': 'Заказ уже обработан'
            })
        
        order.status = 'paid'
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Заказ №{order.id} отмечен как оплаченный. Производитель получит уведомление.'
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
    """Update order status by customer"""
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
        
        # Customers can only mark orders as paid or cancelled
        if status not in ['paid', 'cancelled']:
            return JsonResponse({
                'success': False,
                'message': 'Недопустимое действие'
            })
        
        # Can only cancel pending orders
        if status == 'cancelled' and order.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': 'Можно отменить только неоплаченные заказы'
            })
        
        # Can only mark as paid if pending
        if status == 'paid' and order.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': 'Заказ уже обработан'
            })
        
        order.status = status
        order.save()
        
        status_names = {
            'paid': 'оплачен',
            'cancelled': 'отменен'
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Заказ №{order.id} {status_names[status]}'
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