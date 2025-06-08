from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product


class Order(models.Model):
    """Модель заказа (для отслеживания покупок через QR)"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Контактная информация покупателя
    buyer_name = models.CharField(max_length=100, verbose_name='Имя покупателя')
    buyer_phone = models.CharField(max_length=20, verbose_name='Телефон покупателя')
    buyer_email = models.EmailField(blank=True, verbose_name='Email покупателя')
    
    # Информация о доставке (если нужна)
    delivery_address = models.TextField(blank=True, verbose_name='Адрес доставки')
    delivery_notes = models.TextField(blank=True, verbose_name='Примечания к доставке')
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Заказ #{self.id} - {self.product.name} ({self.get_status_display()})"
    
    @property
    def producer(self):
        """Get the producer of this order's product"""
        return self.product.producer
    
    @property
    def days_since_created(self):
        """Get number of days since order was created"""
        return (timezone.now() - self.created_at).days
    
    @property
    def is_recent(self):
        """Check if order was created in last 24 hours"""
        return self.days_since_created == 0
    
    @property
    def needs_attention(self):
        """Check if order needs attention (pending for more than 3 days)"""
        return self.status == 'pending' and self.days_since_created > 3
    
    def save(self, *args, **kwargs):
        """Автоматически рассчитывать общую стоимость и обновлять статистику"""
        # Calculate total price if not set
        if not self.total_price:
            self.total_price = self.product.price * self.quantity
        
        # Track status changes
        old_status = None
        if self.pk:
            try:
                old_order = Order.objects.get(pk=self.pk)
                old_status = old_order.status
            except Order.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Update product sales count when status changes to completed
        if old_status != 'completed' and self.status == 'completed':
            self.product.num_sales += self.quantity
            self.product.save()
        elif old_status == 'completed' and self.status != 'completed':
            # Decrease sales if order was completed but now changed
            self.product.num_sales = max(0, self.product.num_sales - self.quantity)
            self.product.save()
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'paid']
    
    def can_be_marked_paid(self):
        """Check if order can be marked as paid"""
        return self.status == 'pending'
    
    def can_be_completed(self):
        """Check if order can be completed"""
        return self.status == 'paid'
    
    def get_status_color(self):
        """Get bootstrap color class for status"""
        status_colors = {
            'pending': 'warning',
            'paid': 'info',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_status_icon(self):
        """Get bootstrap icon for status"""
        status_icons = {
            'pending': 'bi-clock',
            'paid': 'bi-credit-card',
            'completed': 'bi-check-circle',
            'cancelled': 'bi-x-circle'
        }
        return status_icons.get(self.status, 'bi-question-circle')