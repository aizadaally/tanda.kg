from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Количество товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'producer', 'category', 'price', 'num_sales', 'average_rating_display', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at', 'producer__is_verified']
    search_fields = ['name', 'producer__name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'num_sales']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('producer', 'category', 'name', 'description')
        }),
        ('Цена и изображение', {
            'fields': ('price', 'image')
        }),
        ('Статус и статистика', {
            'fields': ('is_active', 'num_sales', 'created_at', 'updated_at')
        }),
    )
    
    def average_rating_display(self, obj):
        rating = obj.average_rating()
        if rating:
            stars = '★' * int(rating) + '☆' * (5 - int(rating))
            return format_html(f'<span title="{rating:.1f}">{stars}</span>')
        return 'Нет оценок'
    average_rating_display.short_description = 'Рейтинг'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producer', 'category')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at', 'text_preview']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'text']
    readonly_fields = ['created_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Предпросмотр отзыва'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')