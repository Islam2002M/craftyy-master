from pythonic import app, db

# Push an application context to make sure db.create_all() runs within it
with app.app_context():
    # Create all database tables
    db.create_all()
