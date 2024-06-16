# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Product, Order, OrderItem
from app.forms import RegistrationForm, LoginForm, ForgotPasswordForm
from app.emails import send_verification_email, send_password_reset_email
from . import db, login_manager
from sqlalchemy.exc import IntegrityError
from flask import Flask
from flask import session
from app.forms import ResetPasswordForm
from flask import abort
from datetime import datetime
from app.forms import UpdateProfileForm
import hashlib


bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
MERCHANT_ID = '你的商店ID'
HASH_KEY = 'ejCk326UnaZWKisg'
HASH_IV = 'q9jcZX8Ib9LM8wYk'
RETURN_URL = 'https://git.heroku.com/guangtest.git'  # 綠界付款完成後返回的URL
CLIENT_BACK_URL = 'https://git.heroku.com/guangtest.git/checkout'  # 使用者取消付款返回的URL
ORDER_URL = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 綠界測試環境的付款URL

@bp.route('/')
def home():
    category = request.args.get('category', 'all')
    if category == 'all':
        products = Product.query.all()
    else:
        products = Product.query.filter_by(type=category).all()  # 使用 type 字段過濾
    return render_template('home.html', products=products)

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    recommended_products = Product.query.filter(Product.type == product.type, Product.id != product.id).limit(4).all()
    return render_template('product_detail.html', product=product, recommended_products=recommended_products)

@bp.route('/category/<string:category>')
def category(category):
    products = Product.query.filter_by(type=category).all()
    return render_template('category.html', products=products)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('This email address is already registered. Please use a different email.', 'danger')
            return redirect(url_for('main.register'))
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('This username is already taken. Please choose a different username.', 'danger')
            return redirect(url_for('main.register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash('Congratulations, you are now a registered user! Please check your email for verification instructions.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/verify_email/<token>')
def verify_email(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.home'))
    user.email_verified = True
    db.session.commit()
    flash('Your account has been verified!', 'success')
    return redirect(url_for('main.home'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('此信箱尚未被註冊，請先註冊!!!', 'danger')
            return redirect(url_for('main.register'))
        elif user and not user.check_password(form.password.data):
            flash('信箱或密碼有誤，請在確認你的信箱與密碼!!!.', 'danger')
        else:
            login_user(user)
            session['username'] = user.username
            flash('登入成功!!!', 'success')
            return redirect(url_for('main.home'))
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('An email with instructions to reset your password has been sent to your email address.', 'info')
            return redirect(url_for('main.login'))
        else:
            flash('This email address is not registered.', 'danger')
            return redirect(url_for('main.forgot_password'))
    return render_template('forgot_password.html', title='Forgot Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):  
    app.logger.info("Reset password route triggered.")  # 添加日誌
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.verify_reset_token(token)
        if user is None:
            flash('Invalid or expired token.', 'warning')
            return redirect(url_for('main.forgot_password'))
        user.set_password(form.password.data)
        db.session.commit()
        flash('您的密碼重設成功!!!', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', title='Reset Password', form=form , token=token)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.set_password(form.password.data)
        current_user.phone = form.phone.data  # 新增電話
        current_user.address = form.address.data  # 新增地址
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone  # 在 GET 請求中將電話填入表單
        form.address.data = current_user.address  # 在 GET 請求中將地址填入表單
    return render_template('update_profile.html', title='Update Profile', form=form)


@bp.route('/cart')
@login_required
def cart():
    cart_items = []
    total = 0
    if 'cart' in session:
        for item in session['cart']:
            product = Product.query.get(item['product_id'])
            if product:
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'size': item.get('size', 'N/A'),  # 使用 get 方法以防止 KeyError
                    'id': item['id']
                })
                total += int(product.price) * int(item['quantity'])
    return render_template('cart.html', cart_items=cart_items, total=total)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size')
    cart = session.get('cart', [])

    # 檢查購物車中是否已經存在相同的產品，如果存在，增加數量
    for item in cart:
        if item['product_id'] == product.id and item['size'] == size:
            item['quantity'] += quantity
            flash('產品數量已更新')
            session['cart'] = cart
            return redirect(url_for('main.home'))

    # 如果購物車中沒有相同的產品，則新增一個新的項目
    cart.append({
        'product_id': product.id,
        'quantity': quantity,
        'size': size,
        'id': len(cart) + 1
    })
    session['cart'] = cart
    flash('商品已添加到購物車')
    return redirect(url_for('main.home'))


@bp.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    quantity = int(request.form.get('quantity'))
    for item in session['cart']:
        if item['id'] == item_id:
            item['quantity'] = quantity
            break
    session.modified = True
    flash('Cart updated.', 'success')
    return redirect(url_for('main.cart'))

@bp.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
    session.modified = True
    flash('Item removed from cart.', 'success')
    return redirect(url_for('main.cart'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('請先登入')
    return redirect(url_for('main.login'))

@bp.route('/checkout')
@login_required
def checkout():
    cart_items = []
    total = 0
    if 'cart' in session:
        for item in session['cart']:
            product = Product.query.get(item['product_id'])
            if product:
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'size': item.get('size', 'N/A'),
                    'id': item['id']
                })
                total += int(product.price) * int(item['quantity'])
    return render_template('checkout.html', cart_items=cart_items, total=total)

@bp.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        payment_method = request.form['payment_method']
        payment_status = request.form['payment_status']

        # Check if 'cart' exists in session and if it's not empty
        if 'cart' not in session or not session['cart']:
            flash('Your shopping cart is empty!', 'warning')
            return redirect(url_for('main.home'))

        total_amount = 0.0

        try:
            # Calculate total amount
            for item in session['cart']:
                product = Product.query.get(item['product_id'])  # Retrieve product from database
                if product:
                    total_amount += int(product.price) * int(item['quantity'])
        except KeyError:
            flash('There was an error processing your order. Please try again later.', 'danger')
            return redirect(url_for('main.home'))

    #     Create a new Order instance
    #     new_order = Order(user_id=current_user.id, total_amount=total_amount, status=payment_status)
    #     db.session.add(new_order)
    #     db.session.commit()

    #     # Get the newly created order's id
    #     order_id = new_order.id

    #     # Save order details to OrderItem table (assuming you have items in the cart)
    #     for item in session['cart']:
    #         product_id = item['product_id']
    #         quantity = item['quantity']
    #         price = Product.query.get(product_id).price  # Retrieve product price from database
    #         order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
    #         db.session.add(order_item)
        
    #     # Clear the shopping cart after the order has been submitted
    #     session.pop('cart', None)

    #     # Commit all changes to the database
    #     db.session.commit()

    #     # Construct the data to be sent to ECPay
    #     data = {
    #         'MerchantID': MERCHANT_ID,
    #         'MerchantTradeNo': str(order_id),
    #         'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
    #         'PaymentType': 'aio',
    #         'TotalAmount': str(total_amount),
    #         'TradeDesc': 'Your trade description',
    #         'ItemName': 'Your item name',
    #         'ReturnURL': RETURN_URL,
    #         'ClientBackURL': CLIENT_BACK_URL,
    #         'ChoosePayment': payment_method,
    #         'EncryptType': '1'
    #     }

    #     # Generate CheckMacValue
    #     data_str = '&'.join([f'{key}={data[key]}' for key in sorted(data)])
    #     check_mac_value = 'HashKey=' + HASH_KEY + '&' + data_str + '&' + 'HashIV=' + HASH_IV
    #     check_mac_value = hashlib.sha256(check_mac_value.encode('utf-8')).hexdigest().upper()

    #     data['CheckMacValue'] = check_mac_value

    #     # Send the request to ECPay
    #     response = requests.post(ORDER_URL, data=data)

    #     # Redirect the user to the payment page
    #     return redirect(response.text)
    # else:
    #     # Handle invalid request method
    #     return "Method not allowed", 405


@admin_bp.before_request
def restrict_to_admins():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route('/')
@login_required
def admin_dashboard():
    return render_template('admin/admin_base.html')

@admin_bp.route('/manage_products')
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    search = request.args.get('search', '')

    if search:
        query = Product.query.filter(Product.name.ilike(f"%{search}%"))
    else:
        query = Product.query

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/manage_products.html', products=products)

@admin_bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        product_type = request.form.get('type')
        price = request.form.get('price')
        photo = request.form.get('photo')

        new_product = Product(name=name, type=product_type, price=price, photo=photo)
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.type = request.form.get('type')
        product.price = request.form.get('price')
        db.session.commit()
        flash('產品已成功更新！', 'success')
        return redirect(url_for('admin.manage_products'))
    return render_template('admin/edit_product.html', product=product)

@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('產品已成功刪除！', 'success')
    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/manage_orders')
@login_required
def manage_orders():
    orders = Order.query.all()
    return render_template('admin/manage_orders.html', orders=orders)

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    username = request.form.get('username')
    email = request.form.get('email')
    user.username = username
    user.email = email
    db.session.commit()
    flash('User updated successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('用戶刪除成功', 'success')
    return redirect(url_for('admin.manage_users'))
