# file for seeding or manual db modifications
from app import app

from faker import Faker
from datetime import datetime, timedelta
from models import db, User, Flight, Seat, Booking
from flask_bcrypt import Bcrypt
from random import choice, randint

bcrypt = Bcrypt(app)

from faker import Faker
from datetime import datetime, timedelta
from models import db, User, Flight, Seat
from flask_bcrypt import Bcrypt
from random import randint

bcrypt = Bcrypt()
fake = Faker()

airlines = [
    "American Airlines",
    "Delta Air Lines",
    "United Airlines",
    "Southwest Airlines",
    "Air Canada",
    "British Airways",
    "Lufthansa",
    "Air France",
    "Emirates",
    "Singapore Airlines"
]

cities = [
    "New York",
    "London",
    "Paris",
    "Tokyo",
    "Sydney",
    "Dubai",
    "Singapore",
    "Toronto",
    "Berlin",
    "Madrid",
    "Rome",
    "Amsterdam",
    "Hong Kong",
    "Shanghai",
    "Mumbai",
    "Cape Town",
    "Rio de Janeiro",
    "Los Angeles",
    "Chicago",
    "San Francisco"
]

def seed_database():
    """Populate the database with mock data using predefined lists."""
    with app.app_context():
        # Clear existing data
        db.session.query(Seat).delete()
        db.session.query(Flight).delete()
        db.session.query(User).delete()

        # Add users
        users = []
        for _ in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            password = "pass"
            users.append(User(
                first_name=first_name,
                last_name=last_name,
                role="user",
                email=email,
                password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            ))
        db.session.add_all(users)

        db.session.commit()

        # Add flights
        flights = []
        for _ in range(20):
            departure_time = fake.date_time_between(start_date="now", end_date="+1y")
            flight_duration_hours = randint(2, 12)  # random flight duration
            arrival_time = departure_time + timedelta(hours=flight_duration_hours)
            origin = choice(cities)
            destination = choice(cities)
            # Ensure origin and destination are not the same
            while destination == origin:
                destination = choice(cities)
            airline = choice(airlines)
            flights.append(Flight(
                flight_number=fake.bothify(text="FL###"),
                departure_time=departure_time,
                arrival_time=arrival_time,
                origin=origin,
                destination=destination,
                airline=airline,
                total_seats=randint(50, 300),
            ))
        db.session.add_all(flights)

        db.session.commit()

        # Add seats
        seats = []
        for flight in flights:
            for i in range(1, 10):
                seats.append(Seat(
                    flight_id=flight.id,
                    seat_number=f"{i}",
                    is_available=True
                ))
        db.session.add_all(seats)

        admin_user = User(
            first_name="Admin",
            last_name="User",
            role="admin",
            email="admin@example.com",
            password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8"),
        )
        db.session.add(admin_user)
        db.session.commit()

        # Commit all changes
        db.session.commit()

        print("Database seeded successfully!")



def show_all_tables():
    #Show all tables and  entries
    with app.app_context():
        tables = db.metadata.tables.keys()
        print("Tables in the database:\n")

        for table_name in tables:
            print(table_name)

            table = db.metadata.tables[table_name]
            rows = db.session.execute(table.select()).fetchall()

            if rows:
                print(f"Columns: {', '.join(table.columns.keys())}")
                for row in rows:
                    print(row)
            else:
                print("No entries found.")
            print("\n")

def clear_tables():
    """Clear all entries from the tables but keep the tables intact."""
    with app.app_context():
        # Get all models and clear data
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        print("All table entries have been cleared.")

def delete_all_tables():
    with app.app_context():
        db.drop_all()
        print("all tables deleted")

if __name__ == "__main__":
    # delete_all_tables()
    # with app.app_context():
    #     db.create_all()

    seed_database()
    show_all_tables()
