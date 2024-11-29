# file for seeding or manual db modifications
from datetime import datetime
from app import app
from models import db, User, Flight

def seed_database():
    """Seed the database with initial data."""
    with app.app_context():
        user1 = User(first_name="Jane", last_name="Doe", email="alice@example.com", password_hash="pass1")
        user2 = User(first_name="John", last_name="Pork", email="John@example.com", password_hash="pass2")
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

        # Commit data to the database
        db.session.add_all([user1, user2, flight1, flight2])
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

def delete_all_tables():
    with app.app_context():
        db.drop_all()
        print("all tables deleted")

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()

    # seed_database()
    show_all_tables()
    # delete_all_tables()
