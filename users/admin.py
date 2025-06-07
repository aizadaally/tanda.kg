from django.contrib import admin
from django.utils.html import format_html
from .models import Producer, StoreLocation


class StoreLocationInline(admin.TabularInline):
    model = StoreLocation
    extra = 1


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'region', 'is_verified', 'created_at', 'products_count']
    list_filter = ['is_verified', 'region', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    list_editable = ['is_verified']
    inlines = [StoreLocationInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'description', 'region')
        }),
        ('Медиа', {
            'fields': ('logo', 'qr_code')
        }),
        ('Контакты и сайт', {
            'fields': ('website',)
        }),
        ('Статус', {
            'fields': ('is_verified', 'created_at')
        }),
    )
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Количество товаров'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'producer', 'city', 'address', 'phone']
    list_filter = ['city']
    search_fields = ['name', 'producer__name', 'address']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producer')