from app import db
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer  as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20)) 
    address = db.Column(db.String(200))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='user', lazy=True)  

    def get_reset_token(self, expires_in=600):
        print(f"SECRET_KEY: {current_app.config['SECRET_KEY']}")  
        s = Serializer(current_app.config['SECRET_KEY'], salt='your-salt-value')
        token = s.dumps({'user_id': self.id})
        print(f"Generated token: {token}")  
        return token

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def verify_reset_token(token):
        print(f"SECRET_KEY: {current_app.config['SECRET_KEY']}")  # 添加调试信息
        s = Serializer(current_app.config['SECRET_KEY'], salt='your-salt-value')
        try:
            user_id = s.loads(token)['user_id']
            print(f"Decoded user_id: {user_id}")  # 添加调试信息
        except Exception as e:
            print(f"Error decoding token: {e}")  # 添加调试信息
            return None
        return User.query.get(user_id)

class Product(db.Model):
    __tablename__ = 'products'  # 表名应全部小写
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(64), index=True)
    
    def __repr__(self):
        return f"Product('{self.name}', '{self.photo}', '{self.price}', '{self.type}')"
   
class Order(db.Model):
    __tablename__ = 'order'  # 添加表名
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_item'  # 添加表名
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
