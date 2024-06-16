from app import db, create_app
from app.models import User
import pymysql

app = create_app()
pymysql.install_as_MySQLdb()

with app.app_context():
    db.create_all()
    
    # 查找已存在的用戶
    user = User.query.filter_by(email='xpuaz45068@gmail.com').first()
    if user:
        # 更新密碼
        user.set_password('1234567890')
    else:
        # 如果用戶不存在，則創建新用戶
        user = User(username='admin', email='xpuaz45068@gmail.com')
        user.set_password('1234567890')
        db.session.add(user)
        # 設置為管理員
        user.is_admin = True
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
