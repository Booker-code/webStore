import os
import secrets
import string
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL') or 'mysql+pymysql://root:1234567890@localhost/project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'xpuaz45068@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'vqeo zpzq omor uijv'
    MAIL_DEFAULT_SENDER = 'xpuaz45068@gmail.com' 
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    
config = Config()
