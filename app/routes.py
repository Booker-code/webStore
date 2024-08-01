# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Product, Order,OrderItem
from app.forms import RegistrationForm, LoginForm, ForgotPasswordForm,ContactForm
from app.emails import send_verification_email, send_password_reset_email,send_contact_email
from . import db, login_manager
from flask import session,abort
from app.forms import ResetPasswordForm
from app.forms import UpdateProfileForm
import urllib.parse
import hashlib
from datetime import datetime
import random

bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
MERCHANT_ID = '3002607'
HASH_KEY = 'pwFHCqoQZGmho4w6'
HASH_IV = 'EkRm7iFT261dpevs'

CLIENT_BACK_URL = 'https://xietest-756a0f33c6db.herokuapp.com/checkout'  
ORDER_URL = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  

"""---------------------------------------首頁相關設定---------------------------------------"""
@bp.route('/')
def home():
    category = request.args.get('category', 'all')
    if category == 'all':
        products = Product.query.all()
    else:
        products = Product.query.filter_by(type=category).all()

    all_products = Product.query.all()
    if len(all_products) > 8:
        recommended_products = set()
        while len(recommended_products) < 8:
            recommended_products.add(random.choice(all_products))
        recommended_products = list(recommended_products)
    else:
        recommended_products = all_products

    return render_template('home.html', products=products, recommended_products=recommended_products)


@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    recommended_products = Product.query.filter(Product.type == product.type, Product.id != product.id).limit(4).all()
    return render_template('product_detail.html', product=product, recommended_products=recommended_products)

@bp.route('/category/<string:category>')
def category(category):
    products = Product.query.filter_by(type=category).all()
    return render_template('category.html', products=products)

"""---------------------------------------註冊系統---------------------------------------"""
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    try:
        if form.validate_on_submit():
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('This email address is already registered. Please use a different email.', 'danger')
                return redirect(url_for('main.register'))
            
            existing_username = User.query.filter_by(username=form.username.data).first()
            if existing_username:
                flash('This username is already taken. Please choose a different username.', 'danger')
                return redirect(url_for('main.register'))
            
            verification_code = generate_verification_code()
            user = User(username=form.username.data, email=form.email.data,address=form.address.data,phone=form.phone.data, verification_code=verification_code)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            send_verification_email(user)
            
            flash('Congratulations, you are now a registered user! Please check your email for verification instructions.', 'success')
            return redirect(url_for('main.verify_email', email=form.email.data))
        
        return render_template('register.html', title='Register', form=form)
    
    except Exception as e:
        flash(f'Registration failed. Please try again. Error: {str(e)}', 'danger')
        return redirect(url_for('main.register'))

"""---------------------------------------驗證---------------------------------------"""
@bp.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first_or_404()
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        if user.verification_code == verification_code:
            user.email_verified = True
            user.verification_code = None
            db.session.commit()
            flash('Your account has been verified!', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    return render_template('verify_email.html', email=email)

def generate_verification_code(length=6):
    import random
    import string
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

"""---------------------------------------登入系統---------------------------------------"""
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
        elif not user.email_verified:
            flash('Your email is not verified. Please check your email for verification instructions.', 'warning')
            return redirect(url_for('main.verify_email', email=user.email))
        else:
            login_user(user, remember=True)
            session.permanent = True
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
    app.logger.info("Reset password route triggered.")  
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

"""---------------------------------------個人資料更新---------------------------------------"""
@bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.set_password(form.password.data)
        current_user.phone = form.phone.data  
        current_user.address = form.address.data  
        db.session.commit()
        flash('更改成功!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone  
        form.address.data = current_user.address 
    return render_template('update_profile.html', title='Update Profile', form=form)

"""---------------------------------------聯絡我們----------------------------------------------"""
@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if current_user.is_authenticated:
        form.name.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        send_contact_email(name, email, message)
        flash('成功送出表單!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('contact.html', title='Contact Us', form=form)

"""---------------------------------------購物車系統----------------------------------------------"""
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
                    'size': item.get('size', 'N/A'), 
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

  
    for item in cart:
        if item['product_id'] == product.id and item['size'] == size:
            item['quantity'] += quantity
            flash('產品數量已更新')
            session['cart'] = cart
            return redirect(url_for('main.home'))

    cart.append({
        'product_id': product.id,
        'quantity': quantity,
        'size': size,
        'id': len(cart) + 1
    })
    session['cart'] = cart
    flash('商品已添加到購物車')
    return redirect(url_for('main.home'))

#更新數量
@bp.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    quantity = int(request.form.get('quantity'))
    for item in session['cart']:
        if item['id'] == item_id:
            item['quantity'] = quantity
            break
    session.modified = True
    flash('購物車更新.', 'success')
    return redirect(url_for('main.cart'))
#移除
@bp.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
    session.modified = True
    flash('商品已移除.', 'success')
    return redirect(url_for('main.cart'))
#登入確認
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('請先登入')
    return redirect(url_for('main.login'))

"""---------------------------------------結帳介面----------------------------------------------"""
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

def generate_check_mac_value(params, hash_key, hash_iv):
    sorted_params = sorted(params.items())
    encoded_params = urllib.parse.urlencode(sorted_params, safe='()')
    raw = f"HashKey={hash_key}&{encoded_params}&HashIV={hash_iv}"
    encoded_raw = urllib.parse.quote_plus(raw).lower()
    check_mac_value = hashlib.md5(encoded_raw.encode('utf-8')).hexdigest().upper()
    return check_mac_value

"""---------------------------------------綠界結帳SDK----------------------------------------------"""
@bp.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    if 'cart' not in session :
        flash('購物車是空的，無法結帳。', 'error')
        return redirect(url_for('main.checkout'))

    cart_items = []
    total = 0
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
                    
    from datetime import datetime
    import importlib.util
    import os
    relative_path = "app/ecpay_payment_sdk.py"
    absolute_path = os.path.join(os.getcwd(), relative_path)

    spec = importlib.util.spec_from_file_location("ecpay_payment_sdk", absolute_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    order_number = datetime.now().strftime("NO%Y%m%d%H%M%S")
    order_data = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    order_params = {
        'MerchantTradeNo': order_number,
        'StoreID': '',
        'MerchantTradeDate': order_data,
        'PaymentType': 'aio',
        'TotalAmount': total,
        'TradeDesc': '訂單測試',
        'ItemName': product.name,
        'ReturnURL': 'https://www.ecpay.com.tw/return_url.php',
        'ChoosePayment': 'ALL',
        'ClientBackURL': '',
        'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
        'Remark': '交易備註',
        'ChooseSubPayment': '',
        'OrderResultURL': url_for('main.finish_order', _external=True),
        'NeedExtraPaidInfo': 'Y',
        'DeviceSource': '',
        'IgnorePayment': '',
        'PlatformID': '',
        'InvoiceMark': 'N',
        'CustomField1': '',
        'CustomField2': '',
        'CustomField3': '',
        'CustomField4': '',
        'EncryptType': 1,
    }

    extend_params_1 = {
        'ExpireDate': 7,
        'PaymentInfoURL': 'https://www.ecpay.com.tw/payment_info_url.php',
        'ClientRedirectURL': '',
    }

    extend_params_2 = {
        'StoreExpireDate': 15,
        'Desc_1': '',
        'Desc_2': '',
        'Desc_3': '',
        'Desc_4': '',
        'PaymentInfoURL': 'https://www.ecpay.com.tw/payment_info_url.php',
        'ClientRedirectURL': '',
    }

    extend_params_3 = {
        'BindingCard': 0,
        'MerchantMemberID': '',
    }

    extend_params_4 = {
        'Redeem': 'N',
        'UnionPay': 0,
    }

    inv_params = {
    }

    # 建立實體
    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID='3002607',
        HashKey='pwFHCqoQZGmho4w6',
        HashIV='EkRm7iFT261dpevs'
    )

    # 合併延伸參數
    order_params.update(extend_params_1)
    order_params.update(extend_params_2)
    order_params.update(extend_params_3)
    order_params.update(extend_params_4)

    # 合併發票參數
    order_params.update(inv_params)

    try:
        final_order_params = ecpay_payment_sdk.create_order(order_params)
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        return render_template('submit_order.html', service_url=action_url, parameters=final_order_params)
    except Exception as error:
        print('An exception happened: ' + str(error))
        flash('交易過程中發生錯誤，請稍後再試。', 'error')
        import sys
        app.logger.error(f'An exception happened: {error} at line {sys.exc_info()[-1].tb_lineno}', exc_info=True)
        return redirect(url_for('main.home'))

"""---------------------------------------訂單確認、寄送訂單資訊----------------------------------------------"""    
@bp.route('/finish_order', methods=['GET', 'POST'])
@login_required
def finish_order():
    cart_items = []
    total = 0
    order_number = None
    number = []
    try:
        order_number = datetime.now().strftime("NO%Y%m%d%H%M%S")
        session['order_number']=order_number
        if 'cart' in session:
            for item in session['cart']:
                product = Product.query.get(item['product_id'])
                if product:
                    cart_item = {
                        'product': product,
                        'quantity': item['quantity'],
                        'size': item.get('size', 'N/A'),
                        'price': product.price,
                        'subtotal': int(product.price) * int(item['quantity'])
                    }
                    cart_items.append(cart_item)
                    total += cart_item['subtotal']
                    number.append(order_number)
                    
                    new_order = Order(
                        user_id=current_user.id,
                        total_amount=total,
                        status='Pending', 
                        created_at=datetime.now(),
                        size=cart_item['size'],
                        order_number=order_number)
                    db.session.add(new_order)
                    db.session.commit() 
                    for cart_item in cart_items:
                            ot = OrderItem(
                                order_id=new_order.id,
                                product_id=cart_item['product'].id,
                                product_name=cart_item['product'].name,
                                quantity=cart_item['quantity'],
                                size=cart_item['size'],
                                price=cart_item['price'],
                                subtotal=total)
                            db.session.add(ot)
                    db.session.commit()

            from .emails import finishshop
            finishshop(current_user, cart_items, total, order_number)
              
            session.pop('cart', None)
            
            flash('訂單已完成，確認信已發送至您的電子郵件。', 'success')
            return render_template('FinishOrder.html', cart_items=cart_items, order_number=order_number, total=total)

    except Exception as error:
        db.session.rollback()
        app.logger.error(f'An exception happened: {error}', exc_info=True)
        flash('訂單完成過程中發生錯誤。', 'error')

    return redirect(url_for('main.home'))

"""---------------------------------------管理者系統介面----------------------------------------------"""
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

"""---------------------------------------增加新產品----------------------------------------------"""
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

"""---------------------------------------修改產品----------------------------------------------"""
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

"""---------------------------------------刪除產品----------------------------------------------"""
@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('產品已成功刪除！', 'success')
    return redirect(url_for('admin.manage_products'))

"""---------------------------------------訂單管理----------------------------------------------"""
@admin_bp.route('/manage_orders')
@login_required
def manage_orders():
    import sqlite3

    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            o.id, o.total_amount, o.status, o.created_at, o.size, o.order_number, 
            u.username, u.phone, u.address
        FROM "order" o
        JOIN "user" u ON o.user_id = u.id;
    ''')
    orders = cursor.fetchall()

    cursor.execute('''
        SELECT 
            order_id, product_name, quantity, size, price
        FROM order_item
        WHERE order_id IN (SELECT id FROM "order");
    ''')
    order_items = cursor.fetchall()

    order_items_dict = {}
    for item in order_items:
        order_id = item[0]
        if order_id not in order_items_dict:
            order_items_dict[order_id] = []
        order_items_dict[order_id].append({
            'product_name': item[1],
            'quantity': item[2],
            'size': item[3],
            'price': item[4]
        })

    conn.close()
    
    return render_template('admin/manage_orders.html', orders=orders, order_item_dict=order_items_dict)

@admin_bp.route('/order_items/<int:order_id>')
@login_required
def order_items(order_id):
    import sqlite3
    from flask import jsonify
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM order_item WHERE order_id = ?;', (order_id,))
    order_items = cursor.fetchall()

    items = [
        {
            'product_name': item[3],
            'quantity': item[4],
            'size': item[5],
            'price': item[6]
        }
        for item in order_items
    ]

    conn.close()

    return jsonify({'items': items})


@admin_bp.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        flash('Order not found.', 'error')
        return redirect(url_for('admin.manage_orders'))
    try:
        OrderItem.query.filter_by(order_id=order_id).delete()
        db.session.delete(order)
        db.session.commit()
        flash('Order and its items deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'error')
    
    return redirect(url_for('admin.manage_orders'))

"""---------------------------------------用戶管理----------------------------------------------"""
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
