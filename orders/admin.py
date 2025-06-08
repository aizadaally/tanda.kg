from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product_name', 'producer_name', 'buyer_info', 'quantity', 
        'total_price', 'status', 'days_old', 'created_at'
    ]
    list_filter = [
        'status', 'created_at', 'product__category', 'product__producer__region',
        'product__producer__is_verified'
    ]
    search_fields = [
        'product__name', 'user__username', 'user__first_name', 'user__last_name',
        'buyer_name', 'buyer_phone', 'buyer_email', 'product__producer__name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    list_editable = ['status']  # Now matches the field in list_display
    list_per_page = 25
    date_hierarchy = 'created_at'
    
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
        ('Управление производителем', {
            'fields': ('producer_notes', 'estimated_ready_date', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'product__producer', 'user'
        ).prefetch_related('product__category')
    
    def product_name(self, obj):
        return format_html(
            '<a href="/admin/products/product/{}/change/" target="_blank">{}</a>',
            obj.product.id,
            obj.product.name[:40] + ('...' if len(obj.product.name) > 40 else '')
        )
    product_name.short_description = 'Товар'
    product_name.admin_order_field = 'product__name'
    
    def producer_name(self, obj):
        return format_html(
            '<a href="/admin/users/producer/{}/change/" target="_blank">{}</a>{}',
            obj.product.producer.id,
            obj.product.producer.name[:20] + ('...' if len(obj.product.producer.name) > 20 else ''),
            ' ✓' if obj.product.producer.is_verified else ' ⏳'
        )
    producer_name.short_description = 'Производитель'
    producer_name.admin_order_field = 'product__producer__name'
    
    def buyer_info(self, obj):
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>{}',
            obj.buyer_name,
            obj.user.username,
            f'<br/><small>{obj.buyer_phone}</small>' if obj.buyer_phone else ''
        )
    buyer_info.short_description = 'Покупатель'
    
    def days_old(self, obj):
        days = obj.days_since_created
        if days == 0:
            return format_html('<span style="color: green;">Сегодня</span>')
        elif days <= 3:
            return format_html('<span style="color: orange;">{} дн.</span>', days)
        else:
            return format_html('<span style="color: red;">{} дн.</span>', days)
    days_old.short_description = 'Возраст'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='orders_analytics'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Custom analytics view for orders"""
        from datetime import datetime, timedelta
        
        # Get analytics data
        total_orders = Order.objects.count()
        recent_orders = Order.objects.filter(created_at__gte=datetime.now() - timedelta(days=7)).count()
        
        # Orders by status
        status_stats = Order.objects.values('status').annotate(
            count=Count('id'),
            total_revenue=Sum('total_price')
        ).order_by('status')
        
        # Top producers by orders
        top_producers = Order.objects.values(
            'product__producer__name',
            'product__producer__id'
        ).annotate(
            order_count=Count('id'),
            total_revenue=Sum('total_price')
        ).order_by('-order_count')[:10]
        
        # Orders needing attention
        attention_orders = Order.objects.filter(
            Q(status='pending', created_at__lt=datetime.now() - timedelta(days=3)) |
            Q(status='paid', created_at__lt=datetime.now() - timedelta(days=7))
        ).select_related('product', 'product__producer', 'user')[:20]
        
        context = {
            'title': 'Аналитика заказов',
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'status_stats': status_stats,
            'top_producers': top_producers,
            'attention_orders': attention_orders,
        }
        
        return render(request, 'admin/orders/analytics.html', context)
    
    # Custom actions
    actions = ['mark_as_paid', 'mark_as_completed', 'mark_as_cancelled', 'export_orders']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='paid')
        self.message_user(request, f'{updated} заказов отмечено как оплаченные.')
    mark_as_paid.short_description = "Отметить как оплаченные"
    
    def mark_as_completed(self, request, queryset):
        updated = 0
        for order in queryset.filter(status='paid'):
            order.status = 'completed'
            order.save()  # This will trigger the save method to update sales
            updated += 1
        self.message_user(request, f'{updated} заказов отмечено как завершенные.')
    mark_as_completed.short_description = "Отметить как завершенные"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'paid']).update(status='cancelled')
        self.message_user(request, f'{updated} заказов отменено.')
    mark_as_cancelled.short_description = "Отменить заказы"
    
    def export_orders(self, request, queryset):
        """Export selected orders to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        response.write('\ufeff')  # BOM for Excel UTF-8 support
        
        writer = csv.writer(response)
        writer.writerow([
            'ID заказа', 'Дата', 'Товар', 'Производитель', 'Покупатель', 
            'Телефон', 'Email', 'Количество', 'Цена за шт', 'Общая сумма', 'Статус'
        ])
        
        for order in queryset.select_related('product', 'product__producer', 'user'):
            writer.writerow([
                order.id,
                order.created_at.strftime('%d.%m.%Y %H:%M'),
                order.product.name,
                order.product.producer.name,
                order.buyer_name,
                order.buyer_phone,
                order.buyer_email,
                order.quantity,
                float(order.product.price),
                float(order.total_price),
                order.get_status_display()
            ])
        
        return response
    export_orders.short_description = "Экспорт в CSV"
    
    # Override changelist view to show summary
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Add summary statistics
        summary = Order.objects.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_price'),
            pending_orders=Count('id', filter=Q(status='pending')),
            paid_orders=Count('id', filter=Q(status='paid')),
            completed_orders=Count('id', filter=Q(status='completed')),
        )
        
        extra_context['summary'] = summary
        extra_context['analytics_url'] = '/admin/orders/order/analytics/'
        
        return super().changelist_view(request, extra_context)