import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "site.db")}'#'mysql+pymysql://root:1234567890@localhost/project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'xpuaz45068@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'vqeo zpzq omor uijv'
    MAIL_DEFAULT_SENDER = 'xpuaz45068@gmail.com' 
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'your_salt_here'

config = Config()
