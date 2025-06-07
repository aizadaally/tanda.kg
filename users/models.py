from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Producer(models.Model):
    """Модель производителя"""
    
    REGIONS = [
        ('bishkek', 'Бишкек'),
        ('osh', 'Ош'),
        ('jalal-abad', 'Джалал-Абад'),
        ('karakol', 'Каракол'),
        ('naryn', 'Нарын'),
        ('talas', 'Талас'),
        ('batken', 'Баткен'),
        ('other', 'Другой'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=200, verbose_name='Название бренда')
    description = models.TextField(verbose_name='Описание')
    region = models.CharField(max_length=50, choices=REGIONS, verbose_name='Регион')
    logo = models.ImageField(upload_to='producer_logos/', blank=True, null=True, verbose_name='Логотип')
    website = models.URLField(blank=True, null=True, verbose_name='Сайт')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Номер телефона')
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='WhatsApp номер', 
                                      help_text='Например: 996777123456 (без +)')
    is_verified = models.BooleanField(default=False, verbose_name='Подтвержден')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR-код для оплаты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('producer_detail', kwargs={'pk': self.pk})


class StoreLocation(models.Model):
    """Модель офлайн точки продаж"""
    
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='store_locations', verbose_name='Производитель')
    name = models.CharField(max_length=200, verbose_name='Название точки')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    city = models.CharField(max_length=100, verbose_name='Город')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    working_hours = models.CharField(max_length=100, blank=True, verbose_name='Часы работы')
    
    class Meta:
        verbose_name = 'Точка продаж'
        verbose_name_plural = 'Точки продаж'
        
    def __str__(self):
        return f"{self.name} ({self.producer.name})"