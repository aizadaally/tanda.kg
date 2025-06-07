from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm


@login_required
def add_product(request):
    """Add new product (producers only)"""
    # Check if user is a producer
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Только производители могут добавлять товары')
        return redirect('become_producer')
    
    # For testing - allow unverified producers to add products
    # Remove this check later when you want to enforce verification
    # if not producer.is_verified:
    #     messages.warning(request, 'Ваш аккаунт должен быть проверен администратором для добавления товаров')
    #     return redirect('producer_dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.producer = producer
            product.is_active = True
            product.save()
            
            messages.success(request, f'Товар "{product.name}" успешно добавлен!')
            return redirect('producer_dashboard')
        else:
            # Debug form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'producer': producer,
        'categories': Category.objects.all()
    }
    return render(request, 'products/add_product.html', context)


@login_required
def edit_product(request, pk):
    """Edit existing product (producer only)"""
    product = get_object_or_404(Product, pk=pk)
    
    # Check if user owns this product
    if product.producer.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои товары')
        return redirect('producer_dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар "{product.name}" обновлен!')
            return redirect('producer_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'producer': product.producer
    }
    return render(request, 'products/edit_product.html', context)


@login_required
def delete_product(request, pk):
    """Delete product (producer only)"""
    product = get_object_or_404(Product, pk=pk)
    
    # Check if user owns this product
    if product.producer.user != request.user:
        messages.error(request, 'Вы можете удалять только свои товары')
        return redirect('producer_dashboard')
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" удален')
        return redirect('producer_dashboard')
    
    context = {
        'product': product
    }
    return render(request, 'products/delete_product.html', context)


@login_required
def add_review(request, pk):
    """Add review for product"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'Вы уже оставляли отзыв на этот товар')
        return redirect('product_detail', pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product
    }
    return render(request, 'products/add_review.html', context)


@login_required
def edit_review(request, pk):
    """Edit existing review"""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв обновлен!')
            return redirect('product_detail', pk=review.product.pk)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'product': review.product
    }
    return render(request, 'products/edit_review.html', context)


@login_required
def delete_review(request, pk):
    """Delete review"""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    
    if request.method == 'POST':
        product_pk = review.product.pk
        review.delete()
        messages.success(request, 'Отзыв удален')
        return redirect('product_detail', pk=product_pk)
    
    return redirect('product_detail', pk=review.product.pk)


@login_required
def mark_product_sold(request, pk):
    """AJAX endpoint to mark product as sold"""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, pk=pk, is_active=True)
            product.num_sales += 1
            product.save()
            
            return JsonResponse({
                'success': True,
                'new_sales_count': product.num_sales,
                'message': 'Продажа зафиксирована!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})