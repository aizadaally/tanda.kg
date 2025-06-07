from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal

from .models import Cart, CartItem
from products.models import Product


def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__producer').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.total_price,
        'total_items': cart.total_items,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request):
    """AJAX endpoint to add product to cart"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'ID товара не указан'
            })
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item already exists, increase quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} добавлен в корзину',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price),
            'item_total': float(cart_item.get_total_price())
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@require_POST
def update_cart_item(request):
    """AJAX endpoint to update cart item quantity"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'ID товара не указан'
            })
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            item_total = float(cart_item.get_total_price())
        else:
            cart_item.delete()
            item_total = 0
        
        # Refresh cart to get updated totals
        cart.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'message': 'Корзина обновлена',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price),
            'item_total': item_total
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@require_POST
def remove_from_cart(request):
    """AJAX endpoint to remove item from cart"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'ID товара не указан'
            })
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        
        # Refresh cart to get updated totals
        cart.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} удален из корзины',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


def cart_count(request):
    """AJAX endpoint to get cart count"""
    try:
        cart = get_or_create_cart(request)
        return JsonResponse({
            'count': cart.total_items,
            'total': float(cart.total_price)
        })
    except Exception as e:
        return JsonResponse({
            'count': 0,
            'total': 0.0
        })


def clear_cart(request):
    """Clear all items from cart"""
    cart = get_or_create_cart(request)
    cart.clear()
    messages.success(request, 'Корзина очищена')
    return redirect('cart_view')


# Context processor for global cart access
def cart_context(request):
    """Add cart info to all templates"""
    try:
        cart = get_or_create_cart(request)
        return {
            'cart': cart,
            'cart_count': cart.total_items,
            'cart_total': cart.total_price
        }
    except:
        return {
            'cart': None,
            'cart_count': 0,
            'cart_total': 0
        }


# Merge carts when user logs in
def merge_carts(user, session_key):
    """Merge anonymous cart with user cart when user logs in"""
    try:
        # Get session cart
        session_cart = Cart.objects.get(session_key=session_key)
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Move items from session cart to user cart
        for item in session_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                defaults={'quantity': item.quantity}
            )
            if not created:
                user_item.quantity += item.quantity
                user_item.save()
        
        # Delete session cart
        session_cart.delete()
        
    except Cart.DoesNotExist:
        pass  # No session cart to merge