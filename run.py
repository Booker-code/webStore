from app import db, create_app
from app.models import User

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully.")
    
        
        user = User.query.filter_by(email='xpuaz45068@gmail.com').first()
        if user:
       
            user.set_password('1234567890')
        else:
        
            user = User(username='admin', email='xpuaz45068@gmail.com')
            user.set_password('1234567890')
            db.session.add(user)
            
            user.is_admin = True
        db.session.commit()
        print("User created or updated successfully.")
    except Exception as e:
        print(f"Error querying or committing user: {e}")

if __name__ == '__main__':
    app.run(debug=False)
    