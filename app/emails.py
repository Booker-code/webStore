# app/emails.py
from flask_mail import Message
from flask import render_template, url_for, current_app
from . import mail
from itsdangerous import URLSafeTimedSerializer

def send_verification_email(user):
    token = user.get_reset_token()  # 假設這個方法用於獲取驗證令牌
    msg = Message('Email Verification 信箱驗證', sender='xpuaz45068@gmail.com', recipients=[user.email])
    msg.body = f'''To verify your email, visit the following link:
{url_for('main.verify_email', token=token, _external=True)}  
If you did not make this request then simply ignore this email and no changes will be made.
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
If you did not request this email then simply ignore it, no changes will be made.
'''
    mail.send(msg)
   # 進入應用程序上下文並發送郵件
   
