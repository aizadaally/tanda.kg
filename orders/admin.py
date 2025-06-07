from django.contrib import admin
from django.utils.html import format_html
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'product__category']
    search_fields = ['product__name', 'user__username', 'buyer_name', 'buyer_phone']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    list_editable = ['status']
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'product', 'quantity', 'total_price', 'status')
        }),
        ('Контакты покупателя', {
            'fields': ('buyer_name', 'buyer_phone', 'buyer_email')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_notes'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user', 'product__producer')
    
    actions = ['mark_as_paid', 'mark_as_completed']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} заказов отмечено как оплаченные.')
    mark_as_paid.short_description = "Отметить как оплаченные"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заказов отмечено как завершенные.')
    mark_as_completed.short_description = "Отметить как завершенные"