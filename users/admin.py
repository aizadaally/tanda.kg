from django.contrib import admin
from django.utils.html import format_html
from .models import Producer, StoreLocation, UserProfile, Favorite


class StoreLocationInline(admin.TabularInline):
    model = StoreLocation
    extra = 1


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'region', 'is_verified', 'created_at', 'products_count', 'has_qr_code']
    list_filter = ['is_verified', 'region', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    list_editable = ['is_verified']
    inlines = [StoreLocationInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'description', 'region')
        }),
        ('Контакты', {
            'fields': ('phone_number', 'whatsapp_number', 'website')
        }),
        ('Медиа', {
            'fields': ('logo', 'qr_code')
        }),
        ('Статус', {
            'fields': ('is_verified', 'created_at')
        }),
    )
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Количество товаров'
    
    def has_qr_code(self, obj):
        if obj.qr_code:
            return format_html('<span style="color: green;">✓ Есть</span>')
        return format_html('<span style="color: red;">✗ Нет</span>')
    has_qr_code.short_description = 'QR-код'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'producer', 'city', 'address', 'phone']
    list_filter = ['city']
    search_fields = ['name', 'producer__name', 'address']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producer')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'whatsapp_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product', 'product__producer')