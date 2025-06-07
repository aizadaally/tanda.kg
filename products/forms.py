from django import forms
from .models import Product, Category, Review
from users.models import Producer


class ProductForm(forms.ModelForm):
    """Product upload form for producers"""
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название товара (например: Курут домашний)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Подробно опишите ваш товар: состав, способ производства, особенности...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Цена в сомах',
                'min': 1,
                'step': 1
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'name': 'Название товара',
            'category': 'Категория',
            'description': 'Описание товара',
            'price': 'Цена (сомы)',
            'image': 'Фото товара',
        }
        help_texts = {
            'name': 'Краткое и понятное название товара',
            'description': 'Детальное описание поможет покупателям лучше понять ваш товар',
            'price': 'Укажите цену в киргизских сомах',
            'image': 'Загрузите качественное фото товара (JPG, PNG)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories to show only food categories
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = "Выберите категорию"
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля")
        if price and price > 1000000:
            raise forms.ValidationError("Цена не может превышать 1,000,000 сом")
        return price
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 3:
            raise forms.ValidationError("Название должно содержать минимум 3 символа")
        return name.strip() if name else name


class ReviewForm(forms.ModelForm):
    """Review form for customers"""
    
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Поделитесь своим мнением о товаре...'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'Выберите оценку'),
                (5, '5 звезд - Отлично'),
                (4, '4 звезды - Хорошо'),
                (3, '3 звезды - Нормально'),
                (2, '2 звезды - Плохо'),
                (1, '1 звезда - Ужасно'),
            ])
        }
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка',
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise forms.ValidationError("Выберите оценку")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Оценка должна быть от 1 до 5")
        return rating