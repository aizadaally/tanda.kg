from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from .forms import SmartRegistrationForm, ProducerProfileForm


@never_cache
@csrf_protect
def register(request):
    """Smart registration view with proper CSRF"""
    
    if request.method == 'POST':
        form = SmartRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Create user
                user = form.save()
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()
                
                # Create producer profile if needed
                if form.cleaned_data['account_type'] == 'producer':
                    from .models import Producer
                    Producer.objects.create(
                        user=user,
                        name=f"{user.first_name} {user.last_name}",
                        description="Новый производитель на Tanda.kg",
                        region='bishkek',
                        is_verified=False
                    )
                    messages.success(request, f'Аккаунт производителя создан! Войдите в систему.')
                else:
                    messages.success(request, 'Аккаунт покупателя создан! Войдите в систему.')
                
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Ошибка при создании аккаунта: {str(e)}')
        else:
            # Form has errors - they will be displayed in template
            pass
    else:
        form = SmartRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


@login_required
def become_producer(request):
    """Convert regular user to producer"""
    # Check if user is already a producer
    if hasattr(request.user, 'producer'):
        messages.info(request, 'Вы уже являетесь производителем')
        return redirect('producer_dashboard')
    
    if request.method == 'POST':
        # Get form data
        business_name = request.POST.get('business_name')
        description = request.POST.get('description')
        region = request.POST.get('region')
        website = request.POST.get('website')
        
        if not all([business_name, description, region]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'users/become_producer.html')
        
        try:
            from .models import Producer
            Producer.objects.create(
                user=request.user,
                name=business_name,
                description=description,
                region=region,
                website=website or '',
                is_verified=False  # Admin will verify
            )
            
            messages.success(request, 'Заявка на статус производителя отправлена! Ожидайте проверки администратора.')
            return redirect('producer_dashboard')
            
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return render(request, 'users/become_producer.html')
    
    # Show form
    from .models import Producer
    regions = Producer.REGIONS
    return render(request, 'users/become_producer.html', {'regions': regions})


@login_required
def producer_dashboard(request):
    """Producer dashboard"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    # Get producer's products
    try:
        from products.models import Product
        products = Product.objects.filter(producer=producer).order_by('-created_at')
        total_products = products.count()
        total_sales = sum(product.num_sales for product in products)
    except:
        products = []
        total_products = 0
        total_sales = 0
    
    context = {
        'producer': producer,
        'products': products,
        'total_products': total_products,
        'total_sales': total_sales,
    }
    return render(request, 'users/producer_dashboard.html', context)


@login_required
def edit_producer_profile(request):
    """Edit producer profile"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    if request.method == 'POST':
        form = ProducerProfileForm(request.POST, request.FILES, instance=producer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('producer_dashboard')
    else:
        form = ProducerProfileForm(instance=producer)
    
    context = {
        'form': form,
        'producer': producer,
    }
    return render(request, 'users/edit_producer_profile.html', context)


# Store location management stubs
@login_required
def add_store_location(request):
    return HttpResponse("Add store location page - Coming soon!")

@login_required
def edit_store_location(request, pk):
    return HttpResponse("Edit store location page - Coming soon!")

@login_required
def delete_store_location(request, pk):
    return HttpResponse("Delete store location - Coming soon!")


def become_producer(request):
    """Convert regular user to producer"""
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему, чтобы стать производителем')
        return redirect('login')
    
    # Check if user is already a producer
    if hasattr(request.user, 'producer'):
        messages.info(request, 'Вы уже являетесь производителем')
        return redirect('producer_dashboard')
    
    if request.method == 'POST':
        # Get form data
        business_name = request.POST.get('business_name')
        description = request.POST.get('description')
        region = request.POST.get('region')
        website = request.POST.get('website')
        
        if not all([business_name, description, region]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'users/become_producer.html')
        
        try:
            from .models import Producer
            Producer.objects.create(
                user=request.user,
                name=business_name,
                description=description,
                region=region,
                website=website or '',
                is_verified=False  # Admin will verify
            )
            
            messages.success(request, 'Заявка на статус производителя отправлена! Ожидайте проверки администратора.')
            return redirect('producer_dashboard')
            
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return render(request, 'users/become_producer.html')
    
    # Show form
    from .models import Producer
    regions = Producer.REGIONS
    return render(request, 'users/become_producer.html', {'regions': regions})


@login_required
def producer_dashboard(request):
    """Producer dashboard"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    # Get producer's products
    try:
        from products.models import Product
        products = Product.objects.filter(producer=producer).order_by('-created_at')
        total_products = products.count()
        total_sales = sum(product.num_sales for product in products)
    except:
        products = []
        total_products = 0
        total_sales = 0
    
    context = {
        'producer': producer,
        'products': products,
        'total_products': total_products,
        'total_sales': total_sales,
    }
    return render(request, 'users/producer_dashboard.html', context)


@login_required
def edit_producer_profile(request):
    """Edit producer profile"""
    try:
        producer = request.user.producer
    except:
        messages.error(request, 'Вы не являетесь производителем')
        return redirect('become_producer')
    
    if request.method == 'POST':
        # Update producer info
        producer.name = request.POST.get('name', producer.name)
        producer.description = request.POST.get('description', producer.description)
        producer.region = request.POST.get('region', producer.region)
        producer.website = request.POST.get('website', producer.website)
        
        # Handle file uploads
        if 'logo' in request.FILES:
            producer.logo = request.FILES['logo']
        if 'qr_code' in request.FILES:
            producer.qr_code = request.FILES['qr_code']
        
        producer.save()
        messages.success(request, 'Профиль обновлен!')
        return redirect('producer_dashboard')
    
    from .models import Producer
    regions = Producer.REGIONS
    context = {
        'producer': producer,
        'regions': regions,
    }
    return render(request, 'users/edit_producer_profile.html', context)


# Store location management stubs
@login_required
def add_store_location(request):
    return HttpResponse("Add store location page - Coming soon!")

@login_required
def edit_store_location(request, pk):
    return HttpResponse("Edit store location page - Coming soon!")

@login_required
def delete_store_location(request, pk):
    return HttpResponse("Delete store location - Coming soon!")