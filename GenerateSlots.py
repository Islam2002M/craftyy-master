from datetime import datetime, timedelta
from flask import Flask
from pythonic import db
from pythonic.models import Slot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonic.db'  # Replace with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to avoid the KeyError

db.init_app(app)

def generate_slots_and_insert(availability):
    with app.app_context():
        for entry in availability:
            id, start_time_str, end_time_str, days_str, owner_id = entry
            days = days_str.lower().split(', ')
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()

            start_date = datetime.today()
            end_date = start_date + timedelta(days=30)

            current_date = start_date
            while current_date <= end_date:
                day_name = current_date.strftime('%A').lower()
                if day_name in days:
                    current_time = datetime.combine(current_date, start_time)
                    end_time_today = datetime.combine(current_date, end_time)
                    slot_duration = timedelta(minutes=60)

                    while current_time + slot_duration <= end_time_today:
                        period = f"{current_time.time()}-{(current_time + slot_duration).time()}"
                        slot = Slot(
                            period=period,
                            duration=60,
                            availability_id=id,
                            is_available=1,  # Assuming new slots are available by default
                            date=current_date.date()
                        )
                        db.session.add(slot)
                        current_time += slot_duration
                current_date += timedelta(days=1)
        db.session.commit()

availability = [
        (37, '09:00:00', '17:00:00', 'tuesday, thursday', 36),
    (38, '09:00:00', '17:00:00', 'tuesday, thursday', 37),
    (39, '10:00:00', '18:00:00', 'tuesday, thursday', 38),
    (40, '07:00:00', '15:00:00', 'tuesday, thursday, saturday', 39),
    (41, '10:00:00', '18:00:00', 'tuesday, thursday', 40),
    (42, '09:00:00', '17:00:00', 'tuesday, thursday', 41),
    (43, '10:00:00', '18:00:00', 'monday, wednesday, friday', 42),
    (44, '09:00:00', '17:00:00', 'tuesday, thursday', 43),
    (45, '10:00:00', '18:00:00', 'wednesday, saturday', 44),
    (46, '07:00:00', '15:00:00', 'tuesday, thursday', 45),
    (47, '10:00:00', '18:00:00', 'tuesday, thursday', 46),
    (48, '09:00:00', '17:00:00', 'tuesday, thursday', 47),
    (49, '10:00:00', '18:00:00', 'tuesday, thursday', 48),
    (50, '09:00:00', '17:00:00', 'monday, wednesday, friday', 49),
    (51, '10:00:00', '18:00:00', 'tuesday, thursday', 50),
    (52, '07:00:00', '15:00:00', 'tuesday, thursday', 51),
    (53, '10:00:00', '18:00:00', 'tuesday, thursday, saturday', 52),
    (54, '09:00:00', '17:00:00', 'tuesday, thursday', 53),
    (55, '10:00:00', '18:00:00', 'tuesday, thursday', 54),
    (56, '12:00:00', '20:00:00', 'wednesday, saturday', 55),
    (57, '10:00:00', '18:00:00', 'monday, wednesday, friday', 56),
    (58, '07:00:00', '15:00:00', 'tuesday, thursday', 57),
    (59, '10:00:00', '18:00:00', 'tuesday, thursday', 58),
    (60, '09:00:00', '17:00:00', 'tuesday, thursday', 59),
    (61, '10:00:00', '18:00:00', 'tuesday, thursday', 60),
    (62, '09:00:00', '17:00:00', 'tuesday, thursday', 61),
    (63, '10:00:00', '18:00:00', 'tuesday, thursday', 62),
    (64, '07:00:00', '15:00:00', 'monday, wednesday, friday', 63),
    (65, '10:00:00', '18:00:00', 'tuesday, thursday', 64),
    (66, '12:00:00', '20:00:00', 'tuesday, thursday, saturday', 65),
    (67, '10:00:00', '18:00:00', 'wednesday, saturday', 66),
    (68, '09:00:00', '17:00:00', 'tuesday, thursday', 67),
    (69, '10:00:00', '18:00:00', 'tuesday, thursday', 68),
    (70, '07:00:00', '15:00:00', 'tuesday, thursday', 69),
    (71, '10:00:00', '18:00:00', 'monday, wednesday, friday', 70),
    (72, '09:00:00', '17:00:00', 'tuesday, thursday', 71),
    (73, '10:00:00', '18:00:00', 'tuesday, thursday', 72),
    (74, '09:00:00', '17:00:00', 'tuesday, thursday', 73),
    (75, '10:00:00', '18:00:00', 'tuesday, thursday', 74),
    (76, '07:00:00', '15:00:00', 'tuesday, thursday', 75),
    (77, '10:00:00', '18:00:00', 'tuesday, thursday', 76),
    (78, '09:00:00', '17:00:00', 'monday, wednesday, friday', 77),
    (79, '10:00:00', '18:00:00', 'tuesday, thursday, saturday', 78),
    (80, '09:00:00', '17:00:00', 'tuesday, thursday', 79),
    (81, '10:00:00', '18:00:00', 'tuesday, thursday', 80),
    (82, '07:00:00', '15:00:00', 'tuesday, thursday', 81),
    (83, '10:00:00', '18:00:00', 'tuesday, thursday', 82),
    (84, '09:00:00', '17:00:00', 'tuesday, thursday', 83),
    (85, '10:00:00', '18:00:00', 'monday, wednesday, friday', 84),
    (86, '12:00:00', '20:00:00', 'tuesday, thursday', 85),
    (87, '10:00:00', '18:00:00', 'tuesday, thursday', 86),
    (88, '07:00:00', '15:00:00', 'tuesday, thursday', 87),
    (89, '10:00:00', '18:00:00', 'wednesday, saturday', 88),
    (90, '09:00:00', '17:00:00', 'tuesday, thursday', 89),
    (91, '10:00:00', '18:00:00', 'tuesday, thursday', 90),
    (92, '09:00:00', '17:00:00', 'monday, wednesday, friday', 91),
    (93, '10:00:00', '18:00:00', 'tuesday, thursday', 92),
    (94, '07:00:00', '15:00:00', 'tuesday, thursday', 93),
    (95, '10:00:00', '18:00:00', 'tuesday, thursday', 94),
    (96, '12:00:00', '20:00:00', 'tuesday, thursday', 95),
    (97, '10:00:00', '18:00:00', 'tuesday, thursday', 96),
    (98, '09:00:00', '17:00:00', 'tuesday, thursday', 97),
    (99, '10:00:00', '18:00:00', 'monday, wednesday, friday', 98),
    (100, '07:00:00', '15:00:00', 'wednesday, saturday', 99),
    (101, '10:00:00', '18:00:00', 'tuesday, thursday', 100),
    (102, '09:00:00', '17:00:00', 'tuesday, thursday', 101),
    (103, '10:00:00', '18:00:00', 'tuesday, thursday', 102),
    (104, '09:00:00', '17:00:00', 'tuesday, thursday', 103),
    (105, '10:00:00', '18:00:00', 'tuesday, thursday, saturday', 104),
    (106, '07:00:00', '15:00:00', 'monday, wednesday, friday', 105),
    (107, '10:00:00', '18:00:00', 'tuesday, thursday', 106),
    (108, '09:00:00', '17:00:00', 'tuesday, thursday', 107),
    (109, '10:00:00', '18:00:00', 'tuesday, thursday', 108),
    (110, '09:00:00', '17:00:00', 'tuesday, thursday', 109),
    (111, '10:00:00', '18:00:00', 'wednesday, saturday', 110),
    (112, '07:00:00', '15:00:00', 'tuesday, thursday', 111),
    (113, '10:00:00', '18:00:00', 'monday, wednesday, friday', 112),
    (114, '09:00:00', '17:00:00', 'tuesday, thursday', 113),
    (115, '10:00:00', '18:00:00', 'tuesday, thursday', 114),
    (116, '12:00:00', '20:00:00', 'tuesday, thursday', 115),

]

if __name__ == "__main__":
    generate_slots_and_insert(availability)
