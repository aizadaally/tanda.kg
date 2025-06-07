from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal


class Cart(models.Model):
    """Shopping cart model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
    
    def __str__(self):
        if self.user:
            return f"Корзина {self.user.username}"
        return f"Анонимная корзина {self.session_key}"
    
    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Total price of all items in cart"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual item in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        """Total price for this cart item"""
        return Decimal(self.quantity) * self.product.price
    
    def increase_quantity(self, quantity=1):
        """Increase item quantity"""
        self.quantity += quantity
        self.save()
    
    def decrease_quantity(self, quantity=1):
        """Decrease item quantity"""
        if self.quantity > quantity:
            self.quantity -= quantity
            self.save()
        else:
            self.delete()