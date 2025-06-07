#!/usr/bin/env python
"""
Script to create initial data for Tanda.kg
Run this after migrations: python create_initial_data.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanda_project.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Category
from users.models import Producer


def create_categories():
    """Создание категорий кыргызских продуктов питания"""
    categories = [
        {'name': 'Молочные продукты', 'slug': 'dairy', 'icon': 'cup-hot', 'description': 'Курут, айран, сметана, творог'},
        {'name': 'Мёд и продукты пчеловодства', 'slug': 'honey', 'icon': 'droplet', 'description': 'Горный мёд, прополис, воск'},
        {'name': 'Мясные изделия', 'slug': 'meat', 'icon': 'egg-fried', 'description': 'Чучук, казы, бастурма'},
        {'name': 'Консервы и соленья', 'slug': 'preserves', 'icon': 'jar', 'description': 'Варенье, компоты, соленья'},
        {'name': 'Крупы и мука', 'slug': 'grains', 'icon': 'basket3', 'description': 'Мука, крупы, зерновые'},
        {'name': 'Орехи и сухофрукты', 'slug': 'nuts-dried', 'icon': 'tree', 'description': 'Грецкие орехи, курага, изюм'},
        {'name': 'Травяные чаи', 'slug': 'herbal-tea', 'icon': 'cup-straw', 'description': 'Горные травы, лечебные сборы'},
        {'name': 'Хлебобулочные изделия', 'slug': 'bakery', 'icon': 'cake2', 'description': 'Лепёшки, самса, традиционная выпечка'},
        {'name': 'Сладости', 'slug': 'sweets', 'icon': 'candy', 'description': 'Чак-чак, халва, национальные сладости'},
        {'name': 'Напитки', 'slug': 'drinks', 'icon': 'bottle', 'description': 'Максым, кымыз, соки'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'icon': cat_data['icon'],
                'description': cat_data['description']
            }
        )
        if created:
            print(f"✓ Создана категория: {category.name}")
        else:
            print(f"• Категория уже существует: {category.name}")


def create_admin_user():
    """Создание администратора"""
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@tanda.kg',
            password='admin123',
            first_name='Администратор',
            last_name='Tanda.kg'
        )
        print(f"✓ Создан администратор: {admin.username}")
    else:
        print("• Администратор уже существует")


def create_sample_users():
    """Создание примерных пользователей"""
    sample_users = [
        {
            'username': 'producer1',
            'email': 'producer1@example.com',
            'first_name': 'Айгуль',
            'last_name': 'Бекова',
            'password': 'password123'
        },
        {
            'username': 'producer2',
            'email': 'producer2@example.com',
            'first_name': 'Марат',
            'last_name': 'Токтогулов',
            'password': 'password123'
        },
        {
            'username': 'buyer1',
            'email': 'buyer1@example.com',
            'first_name': 'Жамиля',
            'last_name': 'Садыкова',
            'password': 'password123'
        }
    ]
    
    for user_data in sample_users:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(**user_data)
            print(f"✓ Создан пользователь: {user.username}")
        else:
            print(f"• Пользователь уже существует: {user_data['username']}")


def create_sample_producers():
    """Создание примерных производителей"""
    producers_data = [
        {
            'username': 'producer1',
            'name': 'Кыргыз Боз Уй',
            'description': 'Традиционные кыргызские молочные продукты. Изготавливаем курут, айран, сметану по старинным рецептам.',
            'region': 'bishkek',
            'is_verified': True
        },
        {
            'username': 'producer2',
            'name': 'Талас Мёд',
            'description': 'Натуральный мёд с пасек Таласской области. Горный мёд высшего качества.',
            'region': 'talas',
            'is_verified': True
        }
    ]
    
    for prod_data in producers_data:
        try:
            user = User.objects.get(username=prod_data['username'])
            if not hasattr(user, 'producer'):
                producer = Producer.objects.create(
                    user=user,
                    name=prod_data['name'],
                    description=prod_data['description'],
                    region=prod_data['region'],
                    is_verified=prod_data['is_verified']
                )
                print(f"✓ Создан производитель: {producer.name}")
            else:
                print(f"• Производитель уже существует: {user.username}")
        except User.DoesNotExist:
            print(f"✗ Пользователь {prod_data['username']} не найден")


def create_sample_products():
    """Создание примерных продуктов питания"""
    from products.models import Product, Category
    
    sample_products = [
        {
            'producer': 'producer1',  # Кыргыз Боз Уй
            'category': 'dairy',
            'name': 'Курут домашний',
            'description': 'Традиционный кыргызский курут, изготовленный по старинным рецептам из натурального молока. Богат белком и кальцием.',
            'price': 150,
        },
        {
            'producer': 'producer1',
            'category': 'dairy', 
            'name': 'Айран свежий',
            'description': 'Освежающий кыргызский айран из натурального молока. Идеально утоляет жажду в жаркий день.',
            'price': 80,
        },
        {
            'producer': 'producer2',  # Талас Мёд
            'category': 'honey',
            'name': 'Мёд горный Таласский',
            'description': 'Натуральный мёд с высокогорных пасек Таласской области. Собран с альпийских трав и цветов.',
            'price': 500,
        },
        {
            'producer': 'producer2',
            'category': 'honey',
            'name': 'Прополис натуральный',
            'description': 'Лечебный прополис высшего качества. Укрепляет иммунитет и обладает антибактериальными свойствами.',
            'price': 300,
        },
        {
            'producer': 'producer1',
            'category': 'meat',
            'name': 'Чучук домашний',
            'description': 'Традиционная кыргызская колбаса из конины, изготовленная по семейному рецепту.',
            'price': 800,
        },
        {
            'producer': 'producer2',
            'category': 'nuts-dried',
            'name': 'Грецкие орехи Арсланбоб',
            'description': 'Отборные грецкие орехи из знаменитых ореховых лесов Арсланбоба.',
            'price': 400,
        }
    ]
    
    for product_data in sample_products:
        try:
            # Get producer
            from users.models import Producer
            from django.contrib.auth.models import User
            user = User.objects.get(username=product_data['producer'])
            producer = user.producer
            
            # Get category
            category = Category.objects.get(slug=product_data['category'])
            
            # Create product if it doesn't exist
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                producer=producer,
                defaults={
                    'category': category,
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'is_active': True,
                    'num_sales': 0,
                }
            )
            
            if created:
                print(f"✓ Создан продукт: {product.name}")
            else:
                print(f"• Продукт уже существует: {product.name}")
                
        except Exception as e:
            print(f"✗ Ошибка создания продукта {product_data['name']}: {e}")


def main():
    """Основная функция создания начальных данных"""
    print("🚀 Создание начальных данных для Tanda.kg...")
    print()
    
    print("📁 Создание категорий кыргызских продуктов...")
    create_categories()
    print()
    
    print("👨‍💼 Создание администратора...")
    create_admin_user()
    print()
    
    print("👥 Создание примерных пользователей...")
    create_sample_users()
    print()
    
    print("🏭 Создание примерных производителей...")
    create_sample_producers()
    print()
    
    print("🍯 Создание примерных продуктов питания...")
    create_sample_products()
    print()
    
    print("✅ Готово! Начальные данные созданы.")
    print()
    print("📝 Данные для входа:")
    print("   Администратор - admin:admin123")
    print("   Производитель 1 - producer1:password123 (Кыргыз Боз Уй)")
    print("   Производитель 2 - producer2:password123 (Талас Мёд)")
    print("   Покупатель - buyer1:password123")
    print()
    print("🌐 Запустите сервер: python manage.py runserver")


if __name__ == '__main__':
    main()