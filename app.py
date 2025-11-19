import os
import random
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
app = Flask(__name__)
app.secret_key = 'jp_mobiles_secret_key'  # Change this in production

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
# Renamed DB to ensure fresh creation with new 'quantity' column
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'jpmobiles_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0) # Added Quantity

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)

# ==========================================
# HTML TEMPLATES (Premium Gold/White Theme)
# ==========================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JP Mobiles | Luxury Tech</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --gold-primary: #D4AF37;
            --gold-hover: #C5A028;
            --dark-text: #2c3e50;
            --light-bg: #ffffff;
            --grey-bg: #f9f9f9;
        }
        
        body { 
            background-color: var(--light-bg); 
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
            color: var(--dark-text);
            overflow-x: hidden;
        }

        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 40px, 0); }
            to { opacity: 1; transform: translate3d(0, 0, 0); }
        }
        
        .animate-fade-up {
            animation: fadeInUp 0.8s ease-out forwards;
        }

        /* Navbar */
        .navbar { 
            background-color: white; 
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
            padding: 1rem 0;
        }
        .navbar-brand { 
            font-weight: 700; 
            color: var(--dark-text) !important; 
            letter-spacing: 1px;
            font-size: 1.5rem;
        }
        .navbar-brand i { color: var(--gold-primary); }
        .nav-link { 
            color: #555 !important; 
            font-weight: 500; 
            transition: color 0.3s;
            margin: 0 10px;
        }
        .nav-link:hover { color: var(--gold-primary) !important; }

        /* Buttons */
        .btn-gold { 
            background-color: var(--gold-primary); 
            color: white; 
            border: none; 
            padding: 10px 25px;
            border-radius: 50px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .btn-gold:hover { 
            background-color: var(--gold-hover); 
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(212, 175, 55, 0.3);
            color: white;
        }
        .btn-outline-gold {
            border: 2px solid var(--gold-primary);
            color: var(--gold-primary);
            border-radius: 50px;
            padding: 8px 20px;
            transition: all 0.3s ease;
            background: transparent;
        }
        .btn-outline-gold:hover {
            background-color: var(--gold-primary);
            color: white;
        }

        /* Cards */
        .product-card { 
            border: none; 
            background: white;
            transition: all 0.4s ease; 
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.03);
        }
        .product-card:hover { 
            transform: translateY(-10px); 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
        }
        .card-img-wrapper {
            height: 250px;
            background: var(--grey-bg);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        .card-img-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        .product-card:hover .card-img-wrapper img {
            transform: scale(1.1);
        }
        .card-img-wrapper i {
            color: #ddd;
            transition: all 0.4s ease;
        }

        /* Hero */
        .hero { 
            background: white;
            color: var(--dark-text); 
            padding: 100px 0; 
            position: relative;
        }
        .hero::after {
            content: '';
            position: absolute;
            bottom: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(212,175,55,0.1) 0%, rgba(255,255,255,0) 70%);
            pointer-events: none;
        }
        .display-4 { font-weight: 800; letter-spacing: -1px; }

        /* Footer */
        .footer { 
            background-color: #1a1a1a; 
            color: #888; 
            padding: 60px 0; 
            margin-top: 80px; 
        }
        .footer h5 { color: white; margin-bottom: 20px; }
        .footer a:hover { color: var(--gold-primary) !important; }

        /* Badge */
        .badge-gold { background-color: var(--gold-primary); color: white; }
        
        /* Forms */
        .form-control, .form-select {
            border-radius: 10px;
            padding: 12px;
            border: 1px solid #eee;
            background-color: #fdfdfd;
        }
        .form-control:focus, .form-select:focus {
            border-color: var(--gold-primary);
            box-shadow: 0 0 0 0.2rem rgba(212, 175, 55, 0.25);
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-crown me-2"></i>JP Mobiles
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}#products">Collection</a></li>
                    
                    {% if session.get('admin_logged_in') %}
                        <li class="nav-item"><a class="nav-link text-warning" href="{{ url_for('admin_dashboard') }}">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}">Logout</a></li>
                    {% else %}
                         <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_login') }}"><i class="fas fa-user-shield"></i> Admin</a></li>
                    {% endif %}

                    <li class="nav-item ms-2 position-relative">
                        <a class="btn btn-gold" href="{{ url_for('cart') }}">
                            <i class="fas fa-shopping-bag"></i>
                            {% if session.get('cart') %}
                            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-dark">
                                {{ session['cart']|length }}
                            </span>
                            {% endif %}
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    <div class="container mt-4 sticky-top" style="z-index: 1020; top: 80px;">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'warning' if category == 'error' else 'success' }} alert-dismissible fade show shadow-sm border-0" role="alert">
                        {% if category == 'success' %}<i class="fas fa-check-circle me-2"></i>{% else %}<i class="fas fa-exclamation-circle me-2"></i>{% endif %}
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Main Content -->
    {% block content %}{% endblock %}

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-4">
                    <h5>JP Mobiles</h5>
                    <p>Curating the finest mobile accessories for the discerning individual. Experience luxury in every interaction.</p>
                </div>
                <div class="col-md-4 mb-4">
                    <h5>Support</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-decoration-none text-secondary">Shipping Policy</a></li>
                        <li><a href="#" class="text-decoration-none text-secondary">Returns & Exchanges</a></li>
                        <li><a href="{{ url_for('admin_register') }}" class="text-decoration-none text-secondary">Admin Registration</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Follow Us</h5>
                    <div class="fs-5">
                        <a href="#" class="text-secondary me-3"><i class="fab fa-facebook-f"></i></a>
                        <a href="#" class="text-secondary me-3"><i class="fab fa-instagram"></i></a>
                        <a href="#" class="text-secondary"><i class="fab fa-twitter"></i></a>
                    </div>
                </div>
            </div>
            <hr class="border-secondary my-4">
            <div class="text-center small text-secondary">
                &copy; 2025 JP Mobiles Luxury Accessories. All Rights Reserved.
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

HOME_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
<div class="hero text-center animate-fade-up">
    <div class="container">
        <h1 class="display-4 mb-3">Elevate Your Everyday</h1>
        <p class="lead text-muted mb-4">Discover our exclusive collection of premium mobile accessories.</p>
        <a href="#products" class="btn btn-gold btn-lg shadow">Explore Collection</a>
    </div>
</div>

<div class="container mb-5" id="products">
    <div class="text-center mb-5 animate-fade-up" style="animation-delay: 0.2s;">
        <h6 class="text-uppercase text-warning fw-bold letter-spacing-2">Our Selection</h6>
        <h2 class="fw-bold">Featured Products</h2>
        <div style="width: 50px; height: 3px; background: #D4AF37; margin: 15px auto;"></div>
    </div>

    <div class="row row-cols-1 row-cols-md-3 g-4">
        {% for product in products %}
        <div class="col animate-fade-up" style="animation-delay: {{ loop.index * 0.1 }}s;">
            <div class="product-card h-100 d-flex flex-column">
                <div class="card-img-wrapper">
                    {% if product.image_url.startswith('http') %}
                        <img src="{{ product.image_url }}" alt="{{ product.name }}">
                    {% else %}
                        <img src="{{ url_for('uploaded_file', filename=product.image_url) }}" alt="{{ product.name }}">
                    {% endif %}
                    <span class="position-absolute top-0 end-0 m-3 badge bg-white text-dark shadow-sm">{{ product.category }}</span>
                    {% if product.quantity < 1 %}
                        <span class="position-absolute bottom-0 start-0 m-3 badge bg-danger shadow-sm">Out of Stock</span>
                    {% endif %}
                </div>
                <div class="card-body d-flex flex-column p-4">
                    <h5 class="card-title fw-bold mb-2">{{ product.name }}</h5>
                    <p class="card-text text-muted small mb-4">{{ product.description }}</p>
                    
                    <div class="mt-auto d-flex justify-content-between align-items-center">
                        <h4 class="text-dark mb-0 fw-bold">${{ "%.2f"|format(product.price) }}</h4>
                        
                        {% if product.quantity > 0 %}
                        <form action="{{ url_for('add_to_cart', product_id=product.id) }}" method="POST">
                            <button type="submit" class="btn btn-outline-gold rounded-circle p-2" style="width: 45px; height: 45px;">
                                <i class="fas fa-plus"></i>
                            </button>
                        </form>
                        {% else %}
                            <button class="btn btn-light disabled rounded-circle p-2" style="width: 45px; height: 45px;">
                                <i class="fas fa-ban"></i>
                            </button>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

CART_TEMPLATE = """
{% extends "base.html" %}

{% block content %}
<div class="container py-5 animate-fade-up">
    <h2 class="mb-4 fw-bold text-center">Your Selection</h2>
    
    {% if not cart_items %}
        <div class="text-center py-5">
            <div class="mb-4 text-muted"><i class="fas fa-shopping-bag fa-4x"></i></div>
            <h3 class="fw-light">Your bag is empty</h3>
            <p class="text-muted">Explore our collection to find your perfect accessory.</p>
            <a href="{{ url_for('index') }}" class="btn btn-gold mt-3">Start Shopping</a>
        </div>
    {% else %}
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-body p-0">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="bg-light">
                                <tr>
                                    <th class="border-0 ps-4 py-3">Product</th>
                                    <th class="border-0 py-3">Price</th>
                                    <th class="border-0 text-end pe-4 py-3">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in cart_items %}
                                <tr>
                                    <td class="ps-4 py-3">
                                        <div class="d-flex align-items-center">
                                            <div class="rounded bg-light p-2 me-3 text-center text-warning" style="width: 40px; height: 40px; overflow:hidden;">
                                                {% if item.image_url.startswith('http') %}
                                                    <img src="{{ item.image_url }}" style="width:100%; height:100%; object-fit:cover;">
                                                {% else %}
                                                    <img src="{{ url_for('uploaded_file', filename=item.image_url) }}" style="width:100%; height:100%; object-fit:cover;">
                                                {% endif %}
                                            </div>
                                            <div>
                                                <h6 class="mb-0 fw-bold">{{ item.name }}</h6>
                                                <small class="text-muted">{{ item.category }}</small>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="fw-bold">${{ "%.2f"|format(item.price) }}</td>
                                    <td class="text-end pe-4">
                                        <form action="{{ url_for('remove_from_cart', product_id=item.id) }}" method="POST">
                                            <button type="submit" class="btn btn-link text-danger p-0"><i class="fas fa-times"></i></button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="card border-0 shadow-sm">
                    <div class="card-body p-4">
                        <div class="d-flex justify-content-between mb-3">
                            <span class="text-muted">Subtotal</span>
                            <span class="fw-bold">${{ "%.2f"|format(total) }}</span>
                        </div>
                        <hr class="my-3">
                        <div class="d-flex justify-content-between mb-4">
                            <span class="h5 fw-bold">Total</span>
                            <span class="h4 fw-bold text-warning">${{ "%.2f"|format(total) }}</span>
                        </div>
                        <a href="{{ url_for('checkout') }}" class="btn btn-gold w-100 py-3">Secure Checkout</a>
                    </div>
                </div>
            </div>
        </div>
    {% endif %}
</div>
{% endblock %}
"""

AUTH_TEMPLATE = """
{% extends "base.html" %}
{% block content %}
<div class="container py-5 animate-fade-up">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card border-0 shadow-lg">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-user-shield fa-3x text-warning mb-3"></i>
                        <h3 class="fw-bold">{{ title }}</h3>
                        <p class="text-muted">{{ subtitle }}</p>
                    </div>
                    
                    <form method="POST">
                        {% if show_username %}
                        <div class="mb-3">
                            <label class="form-label small text-muted">Username</label>
                            <input type="text" name="username" class="form-control" required>
                        </div>
                        {% endif %}
                        
                        {% if show_phone %}
                        <div class="mb-3">
                            <label class="form-label small text-muted">Mobile Number (for OTP)</label>
                            <input type="tel" name="mobile_number" class="form-control" placeholder="+1234567890" required>
                        </div>
                        {% endif %}

                        {% if show_password %}
                        <div class="mb-3">
                            <label class="form-label small text-muted">Password</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        {% endif %}

                        {% if show_otp %}
                        <div class="mb-4">
                            <label class="form-label small text-muted fw-bold">Enter OTP sent to mobile</label>
                            <input type="text" name="otp" class="form-control text-center fw-bold fs-4" maxlength="6" placeholder="000000" required autofocus>
                            <div class="form-text text-center mt-2 text-warning">
                                <small>Check your phone (console log) for the code</small>
                            </div>
                        </div>
                        {% endif %}

                        <button type="submit" class="btn btn-gold w-100 py-2">{{ btn_text }}</button>
                    </form>
                    
                    {% if link_url %}
                    <div class="text-center mt-3">
                        <a href="{{ link_url }}" class="small text-decoration-none text-muted">{{ link_text }}</a>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

DASHBOARD_TEMPLATE = """
{% extends "base.html" %}
{% block content %}
<div class="container py-5 animate-fade-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="fw-bold">Admin Dashboard</h2>
            <p class="text-muted">Manage inventory and products.</p>
        </div>
        <button class="btn btn-gold" data-bs-toggle="modal" data-bs-target="#addProductModal">
            <i class="fas fa-plus me-2"></i> Add Accessory
        </button>
    </div>

    <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
            <table class="table table-hover align-middle mb-0">
                <thead class="bg-light">
                    <tr>
                        <th class="ps-4 py-3">Image</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th class="text-end pe-4">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in products %}
                    <tr>
                        <td class="ps-4">
                            <div style="width: 40px; height: 40px; overflow:hidden;" class="rounded bg-light border">
                            {% if product.image_url.startswith('http') %}
                                <img src="{{ product.image_url }}" style="width:100%; height:100%; object-fit:cover;">
                            {% else %}
                                <img src="{{ url_for('uploaded_file', filename=product.image_url) }}" style="width:100%; height:100%; object-fit:cover;">
                            {% endif %}
                            </div>
                        </td>
                        <td class="fw-bold">{{ product.name }}</td>
                        <td><span class="badge bg-light text-dark border">{{ product.category }}</span></td>
                        <td>
                            {% if product.quantity < 5 %}
                                <span class="text-danger fw-bold">{{ product.quantity }}</span>
                            {% else %}
                                <span class="text-success">{{ product.quantity }}</span>
                            {% endif %}
                        </td>
                        <td>${{ product.price }}</td>
                        <td class="text-end pe-4">
                            <button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Add Product Modal -->
<div class="modal fade" id="addProductModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content border-0">
            <div class="modal-header border-0">
                <h5 class="modal-title fw-bold">Add New Accessory</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <!-- ENCTYPE required for file uploads -->
            <form action="{{ url_for('admin_add_product') }}" method="POST" enctype="multipart/form-data">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Product Name</label>
                        <input type="text" name="name" class="form-control" required>
                    </div>
                    
                    <div class="row">
                        <div class="col-4 mb-3">
                            <label class="form-label">Price ($)</label>
                            <input type="number" step="0.01" name="price" class="form-control" required>
                        </div>
                         <div class="col-4 mb-3">
                            <label class="form-label">Qty Available</label>
                            <input type="number" name="quantity" class="form-control" required value="10">
                        </div>
                        <div class="col-4 mb-3">
                            <label class="form-label">Category</label>
                            <select name="category" class="form-select">
                                <option>Cases</option>
                                <option>Audio</option>
                                <option>Power</option>
                                <option>Protection</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Product Image</label>
                        <input type="file" name="image" class="form-control" accept="image/*" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea name="description" class="form-control" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-gold">Add Product</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""

# Checkout Success Template
CHECKOUT_TEMPLATE = """
{% extends "base.html" %}
{% block content %}
<div class="container text-center py-5 animate-fade-up" style="min-height: 60vh;">
    <div class="card border-0 shadow mx-auto p-5" style="max-width: 600px;">
        <div class="text-success mb-4">
            <i class="fas fa-check-circle fa-5x text-warning"></i>
        </div>
        <h1 class="fw-bold">Order Confirmed</h1>
        <p class="lead mt-3">Excellent choice.</p>
        <p class="text-muted">Your premium accessories will be dispatched shortly.</p>
        <hr class="my-4">
        <a href="{{ url_for('index') }}" class="btn btn-gold btn-lg mt-3">Return to Boutique</a>
    </div>
</div>
{% endblock %}
"""

# Helper function
def render_page(content_template, **kwargs):
    full_template = content_template.replace('{% extends "base.html" %}', '')
    final_html = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', full_template)
    return render_template_string(final_html, **kwargs)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def send_otp(mobile_number, otp):
    """
    MOCK SMS GATEWAY
    This simulates sending an SMS. 
    In production, replace this print statement with:
    client.messages.create(body=f"Your OTP is {otp}", from_='+12345', to=mobile_number)
    """
    print("\n" + "="*40)
    print(f" [SMS GATEWAY] SENDING SMS TO: {mobile_number}")
    print(f" [SMS GATEWAY] CONTENT: JP Mobiles Admin OTP is {otp}")
    print("="*40 + "\n")
    return True

# ==========================================
# PUBLIC ROUTES
# ==========================================

@app.route('/')
def index():
    products = Product.query.all()
    return render_page(HOME_TEMPLATE, products=products)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/cart')
def cart():
    cart_ids = session.get('cart', [])
    cart_items = []
    total = 0
    if cart_ids:
        for pid in cart_ids:
            product = Product.query.get(pid)
            if product:
                cart_items.append(product)
                total += product.price
    return render_page(CART_TEMPLATE, cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if product and product.quantity > 0:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product_id)
        session.modified = True
        flash('Item added to your selection.', 'success')
    else:
        flash('Sorry, this item is out of stock.', 'error')
        
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        try:
            session['cart'].remove(product_id)
            session.modified = True
        except ValueError:
            pass
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    session.pop('cart', None)
    return render_page(CHECKOUT_TEMPLATE)

# ==========================================
# ADMIN & AUTH ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile_number']
        
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('admin_register'))
            
        hashed_pw = generate_password_hash(password)
        new_admin = Admin(username=username, password_hash=hashed_pw, mobile_number=mobile)
        db.session.add(new_admin)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('admin_login'))
        
    return render_page(AUTH_TEMPLATE, title="Admin Registration", subtitle="Create your secure credentials", 
                      btn_text="Register", show_username=True, show_password=True, show_phone=True,
                      link_text="Already have an account? Login", link_url=url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            # 1. Credentials OK, Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # 2. Store in session (temporary)
            session['temp_admin_id'] = admin.id
            session['otp'] = otp
            
            # 3. Send Mock SMS
            send_otp(admin.mobile_number, otp)
            
            # Note: Removed OTP from Flash message for security as requested.
            flash(f"OTP Sent to {admin.mobile_number[-4:]}.", 'success')
            
            return redirect(url_for('admin_verify_otp'))
        else:
            flash('Invalid credentials.', 'error')
            
    return render_page(AUTH_TEMPLATE, title="Admin Login", subtitle="Enter your credentials to proceed", 
                      btn_text="Login", show_username=True, show_password=True,
                      link_text="Need an account? Register", link_url=url_for('admin_register'))

@app.route('/admin/verify-otp', methods=['GET', 'POST'])
def admin_verify_otp():
    if 'temp_admin_id' not in session or 'otp' not in session:
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        user_otp = request.form['otp']
        
        if user_otp == session['otp']:
            # Success!
            session['admin_logged_in'] = True
            session['admin_id'] = session['temp_admin_id']
            
            # Cleanup temp session
            session.pop('otp', None)
            session.pop('temp_admin_id', None)
            
            flash('Secure login verified.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            
    return render_page(AUTH_TEMPLATE, title="Security Verification", subtitle="Two-Factor Authentication",
                      btn_text="Verify & Login", show_otp=True)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('admin_login'))
        
    products = Product.query.all()
    return render_page(DASHBOARD_TEMPLATE, products=products)

@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    category = request.form['category']
    desc = request.form['description']
    
    # Handle Image Upload
    file = request.files['image']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = filename
    else:
        image_url = 'default.jpg' # Fallback
    
    new_product = Product(
        name=name, 
        price=price, 
        quantity=quantity, 
        category=category, 
        image_url=image_url, 
        description=desc
    )
    db.session.add(new_product)
    db.session.commit()
    
    flash('Product added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# ==========================================
# DATA SEEDING
# ==========================================
def seed_database():
    if not Product.query.first():
        print("Seeding database with demo data...")
        # Using placeholders from Unsplash Source since we can't assume local files exist yet
        products = [
            Product(name="Gold Plated Bumper", price=199.99, quantity=15, category="Cases", 
                    image_url="https://images.unsplash.com/photo-1603313011101-320f26a4f6f6?w=500", 
                    description="24K gold plating for the ultimate luxury statement."),
            
            Product(name="Marble Wireless Pad", price=89.99, quantity=8, category="Power", 
                    image_url="https://images.unsplash.com/photo-1616348436168-de43ad0db179?w=500", 
                    description="Italian Carrara marble charging stone."),
            
            Product(name="Noise Cancelling Pro", price=249.99, quantity=50, category="Audio", 
                    image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500", 
                    description="Studio quality sound with active noise cancellation."),
            
            Product(name="Leather Folio", price=129.99, quantity=3, category="Cases", 
                    image_url="https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=500", 
                    description="Hand-stitched full-grain leather from Florence.")
        ]
        db.session.add_all(products)
        db.session.commit()
        print("Database seeded.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True)