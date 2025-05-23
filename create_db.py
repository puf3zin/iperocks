from app import create_app, db
from app.models import User, Sector, Block, Boulder, Tag, Attempt

app = create_app()
with app.app_context():
    db.create_all()
    
    # Create an admin user
    admin = User(
        username='pufe',
        email='lucaspufe@gmail.com',
        is_admin=True
    )
    admin.set_password('5bd51184771')
    db.session.add(admin)
    db.session.commit() 