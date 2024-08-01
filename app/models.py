from app import db
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer  as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin,db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20)) 
    address = db.Column(db.String(200))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', back_populates='user', lazy=True)
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    
    def get_reset_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'], salt='your-salt-value')
        token = s.dumps({'user_id': self.id})
        return token

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'], salt='your-salt-value')
        try:
            user_id = s.loads(token)['user_id']
            print(f"Decoded user_id: {user_id}")  
        except Exception as e:
            print(f"Error decoding token: {e}")  
            return None
        return User.query.get(user_id)

class Product(db.Model):
    __tablename__ = 'products'  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(64), index=True)
    
    order_items = db.relationship('OrderItem', back_populates='product')
    
    def __repr__(self):
        return f"Product('{self.name}', '{self.photo}', '{self.price}', '{self.type}')"
  
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    size = db.Column(db.String, nullable=True)  
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order',lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False) 
    product_name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')
