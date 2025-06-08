
# Tanda.kg - Marketplace for Local Producers in Kyrgyzstan


**Tanda.kg** is a comprehensive e-commerce marketplace designed specifically for local producers and manufacturers in Kyrgyzstan. The platform connects customers with verified local businesses, promoting domestic production and supporting the local economy.

## Features

### For Customers
- **Product Catalog** - Browse products from verified local producers
- **Smart Search & Filters** - Find products by category, region, price, and producer
- **Shopping Cart** - Add multiple products and manage orders
- **QR Code Payments** - Pay directly to producers via QR codes
- **Favorites** - Save products for later purchase
- **Order Tracking** - Monitor order status and history
- **Producer Profiles** - View detailed information about local businesses

### For Producers
- **Producer Dashboard** - Comprehensive management interface
- **Product Management** - Add, edit, and manage product listings
- **Order Management** - View, track, and update order statuses
- **Customer Communication** - Direct contact via WhatsApp and phone
- **Sales Analytics** - Track sales, revenue, and performance metrics
- **QR Code Integration** - Upload payment QR codes for direct transactions
- **Profile Customization** - Showcase business information and contact details

### For Administrators
- **User Management** - Manage customers and producers
- **Producer Verification** - Verify and approve producer accounts
- **Content Moderation** - Review and manage product listings
- **Analytics Dashboard** - Platform-wide statistics and insights
- **Order Oversight** - Monitor and manage all transactions

## 🚀 Technology Stack

- **Backend**: Django 5.2 (Python)
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Icons**: Bootstrap Icons
- **Styling**: Custom CSS with modern design patterns
- **Payment**: QR code integration for direct payments

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tanda-kg.git
   cd tanda-kg
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Website: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## 🏗️ Project Structure

```
tanda_project/
├── cart/                   # Shopping cart functionality
├── frontend/              # Main frontend views and templates
├── orders/                # Order management system
├── products/              # Product catalog and management
├── users/                 # User authentication and producer profiles
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── frontend/         # Public-facing pages
│   ├── users/            # User-related pages
│   ├── orders/           # Order management pages
│   └── cart/             # Shopping cart pages
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploads (product images, QR codes)
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file for production settings:

```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/tanda_kg
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Email Configuration (Optional)
For producer notifications, configure SMTP in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 👥 User Roles

### Customer
- Browse and search products
- Add products to cart and favorites
- Place orders and track status
- Pay via QR codes
- Contact producers

### Producer
- Manage product listings
- Process and fulfill orders
- View sales analytics
- Communicate with customers
- Upload QR payment codes

### Administrator
- Verify producer accounts
- Moderate content
- Manage users and orders
- Access platform analytics

## 🛒 Order Workflow

1. **Customer** adds products to cart
2. **Customer** places order
3. **Producer** receives notification
4. **Customer** pays via QR code
5. **Producer** marks order as paid
6. **Producer** fulfills order and marks as completed
7. **Customer** can leave reviews (optional)

## 📱 Mobile Responsive

The platform is fully responsive and optimized for:
- Desktop browsers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🔒 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Secure file uploads
- Input validation and sanitization
- Producer verification system

## 🎨 Customization

### Adding Categories
1. Access admin panel (`/admin/`)
2. Go to Products > Categories
3. Add new categories with icons from Bootstrap Icons

### Regions
Supported regions include:
- Bishkek
- Osh
- Jalal-Abad
- Karakol
- Naryn
- Talas
- Batken

## 🚀 Deployment

### For Production

1. **Set up PostgreSQL database**
2. **Configure environment variables**
3. **Set DEBUG=False in settings**
4. **Configure static files serving**
5. **Set up HTTPS**
6. **Configure email services**

### Recommended Hosting
- DigitalOcean
- Heroku
- AWS
- VPS with Ubuntu/CentOS

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📊 Analytics

The platform includes built-in analytics for:
- Total products and producers
- Order statistics
- Revenue tracking
- Regional performance
- Producer metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or questions:
- Email: support@tanda.kg
- GitHub Issues: [Create an issue](https://github.com/yourusername/tanda-kg/issues)

## 🙏 Acknowledgments

- Built with Django and Bootstrap
- Icons by Bootstrap Icons
- Designed for the Kyrgyzstan market
- Supporting local producers and businesses

## 📈 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support (Kyrgyz, Russian, English)
- [ ] SMS notifications
- [ ] Inventory management
- [ ] Delivery tracking
- [ ] Review and rating system
- [ ] Social media integration
- [ ] API for third-party integrations

---

**Made with ❤️ in Kyrgyzstan for local producers and businesses.**