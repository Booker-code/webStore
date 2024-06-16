# app/utils.py

from flask import current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Message
from . import mail

def generate_verification_token(user_id, expires_sec=1800):
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    return s.dumps({'user_id': user_id}).decode('utf-8')

def send_email(subject, sender, recipients, body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body
    mail.send(msg)

def send_verification_email(user):
    token = generate_verification_token(user.id)
    confirm_url = url_for('main.verify_email', token=token, _external=True)
    subject = "Please Verify Your Email Address"
    sender = current_app.config['MAIL_USERNAME']
    recipients = [user.email]
    body = f"Hello, {user.username}! Please click the following link to verify your email address: {confirm_url}"
    send_email(subject, sender, recipients, body)

def send_order_confirmation_email(user, order):
    subject = "Order Confirmation"
    sender = current_app.config['MAIL_USERNAME']
    recipients = [user.email]
    body = f"Hi {user.username},\n\nThank you for your order! Your order details are as follows:\n\nOrder ID: {order.id}\nTotal Amount: {order.total_amount}\nOrder Status: {order.status}\n\nFor further assistance, please contact us.\n\nBest regards,\nThe Team"
    send_email(subject, sender, recipients, body)
