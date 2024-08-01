# app/emails.py
from flask_mail import Message
from flask import render_template, url_for, current_app
from . import mail
from itsdangerous import URLSafeTimedSerializer

def send_verification_email(user):
    msg = Message('Email Verification 信箱驗證', sender='xpuaz45068@gmail.com', recipients=[user.email])
    msg.body = f'''此信件為您的驗證碼:
{user.verification_code}

若您沒有要求此操作，請無視此信件.
'''
    mail.send(msg)


def generate_password_reset_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    
def send_password_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset 密碼重置', sender='xpuaz45068@gmail.com', recipients=[user.email])
    msg.body = f'''請點擊下面連結來重製你的密碼:
{url_for('main.reset_password', token=token, _external=True)} 
如果您沒有要求此電子郵件，則只需忽略它將不進行任何更改.
'''
    mail.send(msg)
   
def finishshop(user, cart_items, total, order_number):
    msg = Message('Your Order Confirmation', sender='your_email@example.com', recipients=[user.email])
    msg.body = f'謝謝您的購買，這是您的購物明細:\n\n訂單編號: {order_number}\n\n'
    for item in cart_items:
        msg.body += f"{item['product']} x {item['quantity']} - ${item['price']} each, Subtotal: ${item['subtotal']}\n"
    msg.body += f"\n總金額: ${total}\n\n謝謝您的訂單!!"
    mail.send(msg)


def send_contact_email(name, email, message):
    msg = Message('New Contact Us Message', sender='xpuaz45068@gmail.com', recipients=['xpuaz45068@gmail.com'])
    msg.body = f'''You have received a new message from {name} ({email}):{message}'''
    mail.send(msg)