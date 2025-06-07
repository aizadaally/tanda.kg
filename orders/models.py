from django.db import models
from django.contrib.auth.models import User
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
        return f"Заказ #{self.id} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Автоматически рассчитывать общую стоимость"""
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)
        
        # Увеличиваем счетчик продаж если заказ оплачен
        if self.status == 'paid':
            self.product.num_sales += self.quantity
            self.product.save()