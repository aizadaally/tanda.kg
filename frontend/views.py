from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg
from products.models import Product, Category
from users.models import Producer


def home(request):
    """Главная страница с демо данными"""
    
    # Получаем данные из базы или используем заглушки
    try:
        # Популярные товары
        popular_products = Product.objects.filter(is_active=True).order_by('-num_sales')[:8]
        
        # Новые товары
        new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        
        # Категории
        categories = Category.objects.all()[:6]
        
        # Статистика
        total_products = Product.objects.filter(is_active=True).count()
        total_producers = Producer.objects.filter(is_verified=True).count()
        
    except Exception:
        # Если таблицы еще не созданы, используем пустые данные
        popular_products = []
        new_products = []
        categories = []
        total_products = 0
        total_producers = 0

    context = {
        'popular_products': popular_products,
        'new_products': new_products,
        'categories': categories,
        'total_products': total_products,
        'total_producers': total_producers,
    }
    return render(request, 'frontend/home.html', context)


def products(request):
    """Каталог товаров"""
    try:
        products_list = Product.objects.filter(is_active=True).select_related('producer', 'category')
        
        # Фильтры
        category_filter = request.GET.get('category')
        region_filter = request.GET.get('region')
        search_query = request.GET.get('search')
        sort_by = request.GET.get('sort', 'newest')
        
        # Применяем фильтры
        if category_filter:
            products_list = products_list.filter(category__slug=category_filter)
        
        if region_filter:
            products_list = products_list.filter(producer__region=region_filter)
        
        if search_query:
            products_list = products_list.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(producer__name__icontains=search_query)
            )
        
        # Сортировка
        if sort_by == 'popular':
            products_list = products_list.order_by('-num_sales')
        elif sort_by == 'rating':
            products_list = products_list.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort_by == 'price_low':
            products_list = products_list.order_by('price')
        elif sort_by == 'price_high':
            products_list = products_list.order_by('-price')
        else:  # newest
            products_list = products_list.order_by('-created_at')
        
        # Данные для фильтров
        categories = Category.objects.all()
        regions = Producer.REGIONS
        
    except Exception:
        # Если таблицы еще не созданы
        products_list = []
        categories = []
        regions = []
        category_filter = None
        region_filter = None
        search_query = None
        sort_by = 'newest'

    context = {
        'products': products_list,
        'categories': categories,
        'regions': regions,
        'current_category': category_filter,
        'current_region': region_filter,
        'search_query': search_query,
        'current_sort': sort_by,
    }
    return render(request, 'frontend/products.html', context)


def product_detail(request, pk):
    """Детальная страница товара"""
    try:
        product = get_object_or_404(Product, pk=pk, is_active=True)
        reviews = product.reviews.all().select_related('user').order_by('-created_at')
        
        # Похожие товары
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product.pk)[:4]
        
        context = {
            'product': product,
            'reviews': reviews,
            'similar_products': similar_products,
        }
        return render(request, 'frontend/product_detail.html', context)
    except Exception:
        # Если товар не найден или таблицы не созданы
        return render(request, 'frontend/404.html', status=404)


def producers(request):
    """Список производителей"""
    try:
        producers_list = Producer.objects.filter(is_verified=True).order_by('name')
        
        # Фильтр по региону
        region_filter = request.GET.get('region')
        if region_filter:
            producers_list = producers_list.filter(region=region_filter)
        
        regions = Producer.REGIONS
        
    except Exception:
        producers_list = []
        regions = []
        region_filter = None

    context = {
        'producers': producers_list,
        'regions': regions,
        'current_region': region_filter,
    }
    return render(request, 'frontend/producers.html', context)


def producer_detail(request, pk):
    """Детальная страница производителя"""
    try:
        producer = get_object_or_404(Producer, pk=pk, is_verified=True)
        products_list = producer.products.filter(is_active=True).order_by('-created_at')
        store_locations = producer.store_locations.all()
        
        context = {
            'producer': producer,
            'products': products_list,
            'store_locations': store_locations,
        }
        return render(request, 'frontend/producer_detail.html', context)
    except Exception:
        return render(request, 'frontend/404.html', status=404)