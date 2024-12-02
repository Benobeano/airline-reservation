# file for seeding or manual db modifications
from datetime import datetime
from flask_bcrypt import Bcrypt
from app import app
from models import db, User, Flight, Seat, Booking

bcrypt = Bcrypt(app)

def seed_database():
    """Populate the database with mock data."""
    with app.app_context():
        # Clear existing data
        db.session.query(Seat).delete()
        db.session.query(Booking).delete()
        db.session.query(Flight).delete()
        db.session.query(User).delete()
        
        # Add users with hashed passwords
        user1 = User(
            first_name="Alice", 
            last_name="Smith", 
            role="user", 
            email="alice@example.com", 
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'), 
        )
        user2 = User(
            first_name="Bob", 
            last_name="Johnson", 
            role="user",  
            email="bob@example.com", 
            password_hash=bcrypt.generate_password_hash("securepassword").decode('utf-8'), 
        )
        db.session.add_all([user1, user2])

        # Add flights
        flight1 = Flight(
            flight_number="FL123",
            departure_time=datetime.strptime("2024-12-01 10:00:00", "%Y-%m-%d %H:%M:%S"),
            arrival_time=datetime.strptime("2024-12-01 14:00:00", "%Y-%m-%d %H:%M:%S"),
            origin="New York",
            destination="London",
            airline="AirExample",
            total_seats=200
        )
        flight2 = Flight(
            flight_number="FL456",
            departure_time=datetime.strptime("2024-12-02 12:00:00", "%Y-%m-%d %H:%M:%S"),
            arrival_time=datetime.strptime("2024-12-02 16:00:00", "%Y-%m-%d %H:%M:%S"),
            origin="San Francisco",
            destination="Tokyo",
            airline="AirSample",
            total_seats=250
        )
        db.session.add_all([flight1, flight2])

        # Add bookings
        booking1 = Booking(
            user_id=1,  # Alice's ID
            flight_id=1,  # Flight 1's ID
            booking_date=datetime.now(),
            status="CONFIRMED"
        )
        booking2 = Booking(
            user_id=2,  # Bob's ID
            flight_id=2,  # Flight 2's ID
            booking_date=datetime.now(),
            status="CONFIRMED"
        )
        db.session.add_all([booking1, booking2])

        # Add seats
        seats = []
        for i in range(1, 11):
            seats.append(Seat(flight_id=1, seat_number=f"1A-{i}", is_available=True if i % 2 == 0 else False))
        for i in range(1, 11):
            seats.append(Seat(flight_id=2, seat_number=f"2B-{i}", is_available=True if i % 2 != 0 else False))
        db.session.add_all(seats)

        # Commit changes
        db.session.commit()

        print("Database seeded successfully!")


def show_all_tables():
    """Show all tables and  entries"""
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
    # with app.app_context():
    #     db.create_all()

    # seed_database()
    # delete_all_tables()
    show_all_tables()
