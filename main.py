import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "codealpha_super_secret_key_change_in_prod"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "store.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship("Order", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    badge = db.Column(db.String(40), nullable=True)
    image_file = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    stock = db.Column(db.Integer, default=25)
    description = db.Column(db.Text, nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    items_json = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(40), default="Confirmed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- SEED INITIAL DATA ----------------

def seed_database():
    if Product.query.count() == 0:
        sample_products = [
            Product(
                name="PulseWave ANC Wireless Earbuds",
                category="Audio & Earbuds",
                price=59.99,
                old_price=89.99,
                badge="33% OFF",
                image_file="earbuds.jpg",
                image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80",
                stock=30,
                description="Active noise cancellation, 36-hour battery case, and low-latency mode for music and gaming."
            ),
            Product(
                name="ChronoFit AMOLED Smart Watch",
                category="Smart Watches",
                price=129.99,
                old_price=179.99,
                badge="HOT DEAL",
                image_file="watch.jpg",
                image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
                stock=20,
                description="Bright AMOLED display, heart-rate and sleep tracking, water-resistant build, and 10-day battery."
            ),
            Product(
                name="KeyForge 75% Mechanical Keyboard",
                category="Computer & Gaming",
                price=94.50,
                old_price=119.00,
                badge="TOP PICK",
                image_file="keyboard.jpg",
                image_url="https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
                stock=15,
                description="Tactile hot-swappable switches, vibrant per-key RGB lighting, and durable aluminum top plate."
            ),
            Product(
                name="VoltCharge 100W GaN USB-C Hub",
                category="Cables & Chargers",
                price=44.00,
                old_price=59.00,
                badge="FLASH SALE",
                image_file="hub.jpg",
                image_url="https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=800&q=80",
                stock=40,
                description="Fast-charging multi-port USB-C and USB-A hub built for laptops, tablets, and flagship phones."
            ),
            Product(
                name="LumaGlow Desk & Creator Lamp",
                category="Home & Lifestyle",
                price=39.99,
                old_price=54.99,
                badge="NEW",
                image_file="lamp.jpg",
                image_url="https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80",
                stock=25,
                description="Adjustable color temperature and brightness bar with touch controls for study and desk setups."
            ),
            Product(
                name="AeroStride Everyday Pro Sneakers",
                category="Fashion & Wearables",
                price=74.99,
                old_price=99.99,
                badge="TRENDING",
                image_file="sneakers.jpg",
                image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80",
                stock=18,
                description="Breathable mesh upper with cushioned sole designed for all-day comfort and street style."
            ),
            Product(
                name="SnapShot 4K Pocket Action Cam",
                category="Gadgets & Tech",
                price=149.00,
                old_price=199.00,
                badge="SAVE $50",
                image_file="camera.jpg",
                image_url="https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=800&q=80",
                stock=12,
                description="Ultra-HD 4K stabilization, wide-angle lens, and compact body for travel and content creation."
            ),
            Product(
                name="AuraShield Crossbody Tech Sling",
                category="Fashion & Wearables",
                price=34.50,
                old_price=49.00,
                badge="BESTSELLER",
                image_file="bag.jpg",
                image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80",
                stock=35,
                description="Water-repellent fabric with smart organizer pockets for power banks, cables, and daily essentials."
            )
        ]
        db.session.add_all(sample_products)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_database()


# ---------------- HELPER FUNCTIONS ----------------

def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


def get_cart_summary():
    cart = session.get("cart", {})
    items = []
    total_qty = 0
    subtotal = 0.0

    for pid_str, qty in list(cart.items()):
        product = Product.query.get(int(pid_str))
        if product and qty > 0:
            line_total = round(product.price * qty, 2)
            items.append({
                "product": product,
                "quantity": qty,
                "line_total": line_total
            })
            total_qty += qty
            subtotal += line_total
        else:
            del cart[pid_str]

    session["cart"] = cart
    return items, total_qty, round(subtotal, 2)


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    selected_category = request.args.get("category", "All")
    search_query = request.args.get("q", "").strip()

    categories_rows = db.session.query(Product.category).distinct().all()
    categories = ["All"] + [row[0] for row in categories_rows]

    query = Product.query
    if selected_category and selected_category != "All":
        query = query.filter(Product.category == selected_category)
    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            (Product.name.ilike(like_pattern)) | (Product.description.ilike(like_pattern))
        )

    products = query.order_by(Product.id.asc()).all()
    _, cart_count, _ = get_cart_summary()
    current_user = get_current_user()

    return render_template(
        "index.html",
        products=products,
        categories=categories,
        selected_category=selected_category,
        search_query=search_query,
        cart_count=cart_count,
        current_user=current_user
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(
        Product.category == product.category, Product.id != product.id
    ).limit(3).all()
    _, cart_count, _ = get_cart_summary()
    current_user = get_current_user()

    return render_template(
        "product.html",
        product=product,
        related_products=related_products,
        cart_count=cart_count,
        current_user=current_user
    )


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = int(request.form.get("quantity", 1))
    if qty < 1:
        qty = 1

    cart = session.get("cart", {})
    pid_str = str(product.id)
    cart[pid_str] = cart.get(pid_str, 0) + qty
    session["cart"] = cart
    session.modified = True

    flash(f"Added '{product.name}' to your cart!", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    action = request.form.get("action")
    cart = session.get("cart", {})
    pid_str = str(product_id)

    if pid_str in cart:
        if action == "increase":
            cart[pid_str] += 1
        elif action == "decrease":
            cart[pid_str] -= 1
            if cart[pid_str] <= 0:
                del cart[pid_str]
        elif action == "remove":
            del cart[pid_str]

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/cart")
def view_cart():
    items, cart_count, subtotal = get_cart_summary()
    shipping = 0.0 if subtotal == 0 or subtotal >= 100 else 9.99
    grand_total = round(subtotal + shipping, 2)
    current_user = get_current_user()

    return render_template(
        "cart.html",
        cart_items=items,
        cart_count=cart_count,
        subtotal=subtotal,
        shipping=shipping,
        grand_total=grand_total,
        current_user=current_user
    )


@app.route("/checkout", methods=["POST"])
def checkout():
    items, _, subtotal = get_cart_summary()
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("index"))

    current_user = get_current_user()
    customer_name = request.form.get("customer_name", "").strip()
    customer_email = request.form.get("customer_email", "").strip()
    shipping_address = request.form.get("shipping_address", "").strip()

    if current_user:
        if not customer_name:
            customer_name = current_user.name
        if not customer_email:
            customer_email = current_user.email

    if not customer_name or not customer_email or not shipping_address:
        flash("Please fill in your name, email, and shipping address to place the order.", "error")
        return redirect(url_for("view_cart"))

    shipping = 0.0 if subtotal >= 100 else 9.99
    grand_total = round(subtotal + shipping, 2)

    serialized_items = [
        {
            "id": entry["product"].id,
            "name": entry["product"].name,
            "price": entry["product"].price,
            "quantity": entry["quantity"],
            "line_total": entry["line_total"]
        }
        for entry in items
    ]

    new_order = Order(
        user_id=current_user.id if current_user else None,
        customer_name=customer_name,
        customer_email=customer_email,
        shipping_address=shipping_address,
        items_json=json.dumps(serialized_items),
        total_amount=grand_total,
        status="Confirmed"
    )
    db.session.add(new_order)
    db.session.commit()

    session["cart"] = {}
    session.modified = True

    return redirect(url_for("order_confirmation", order_id=new_order.id))


@app.route("/order/<int:order_id>")
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    ordered_items = json.loads(order.items_json)
    _, cart_count, _ = get_cart_summary()
    current_user = get_current_user()

    return render_template(
        "checkout_success.html",
        order=order,
        ordered_items=ordered_items,
        cart_count=cart_count,
        current_user=current_user
    )


@app.route("/orders")
def my_orders():
    current_user = get_current_user()
    if not current_user:
        flash("Please log in to view your account orders.", "error")
        return redirect(url_for("login"))

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    parsed_orders = []
    for o in orders:
        parsed_orders.append({
            "order": o,
            "items": json.loads(o.items_json)
        })

    _, cart_count, _ = get_cart_summary()
    return render_template(
        "orders.html",
        orders_list=parsed_orders,
        cart_count=cart_count,
        current_user=current_user
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user():
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:
            flash("Please provide your name, valid email, and a password (at least 6 characters).", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        flash(f"Welcome to VibeMart, {user.name}! Your account is ready.", "success")
        return redirect(url_for("index"))

    _, cart_count, _ = get_cart_summary()
    return render_template("register.html", cart_count=cart_count, current_user=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    _, cart_count, _ = get_cart_summary()
    return render_template("login.html", cart_count=cart_count, current_user=None)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)