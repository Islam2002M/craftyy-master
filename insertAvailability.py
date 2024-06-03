from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time

from pythonic.models import Availability

# Create a Flask application instance
app = Flask(__name__)

# Configure your Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy to work with your Flask application
db = SQLAlchemy(app)

# # Define your SQLAlchemy model
# class Availability(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     start_time = db.Column(db.Time)
#     end_time = db.Column(db.Time)
#     days = db.Column(db.String(100))
#     owner_id = db.Column(db.Integer)

# Function to insert availability data into the database
def insert_availability():
    # Initialize owner_id
    owner_id = 37
    
    # Loop through availability records
    for i in range(37, 116):
        # Initialize start and end times
        start_time_str = '09:00:00'
        end_time_str = '17:00:00'
        
        # Adjust start and end times based on conditions
        if i % 2 == 0:
            start_time_str = '10:00:00'
            end_time_str = '18:00:00'
        elif i % 3 == 0:
            start_time_str = '07:00:00'
            end_time_str = '15:00:00'
        elif i % 5 == 0:
            start_time_str = '12:00:00'
            end_time_str = '20:00:00'

        # Define days based on conditions
        days = 'tuesday, thursday'
        if i % 7 == 0:
            days = 'monday, wednesday, friday'
        elif i % 11 == 0:
            days = 'wednesday, saturday'
        elif i % 13 == 0:
            days = 'tuesday, thursday, saturday'

        # Convert time strings to Python time objects
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()

        # Insert into the database
        db.session.add(Availability(
            start_time=start_time,
            end_time=end_time,
            days=days,
            owner_id=owner_id
        ))
        
        # Increment owner_id
        owner_id += 1

    # Commit changes to the database
    db.session.commit()

# Ensure the script runs within the Flask application context
if __name__ == '__main__':
    with app.app_context():
        insert_availability()
