from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import Producer


class Category(models.Model):
    """Модель категории товаров"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Слаг')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Иконка (Bootstrap Icons)')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара"""
    
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='products', verbose_name='Производитель')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (сомы)')
    image = models.ImageField(upload_to='product_images/', verbose_name='Фото товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    num_sales = models.PositiveIntegerField(default=0, verbose_name='Количество продаж')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.producer.name}"
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})
    
    def average_rating(self):
        """Средний рейтинг товара"""
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0
    
    def total_reviews(self):
        """Общее количество отзывов"""
        return self.reviews.count()


class Review(models.Model):
    """Модель отзыва"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг (1-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # Один отзыв от пользователя на товар
        
    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"