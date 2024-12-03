from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from forms import LoginForm, SignUpForm
from models import Booking, Flight, User, db
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SECRET_KEY'] = 'a-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airline.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def home():
    user_full_name = None
    user_role = None
    if "user_id" in session:
        user = db.session.get(User, session.get("user_id"))
        if user:
            user_full_name = f"{user.first_name} {user.last_name}"
            user_role = user.role
    return render_template("home.html", user_full_name=user_full_name, user_role=user_role)



@app.route("/search", methods=["GET", "POST"])
def search_flights():
    # Get unique destinations for the dropdown
    destinations = Flight.query.with_entities(Flight.destination).distinct().all()
    destinations = [d[0] for d in destinations]  # Extract values from tuples

    flights = Flight.query.all()  # Display all flights by default

    if request.method == "POST":
        # Retrieve form data
        destination = request.form.get("destination", "").strip()
        travel_date = request.form.get("travel_date")
        seats = request.form.get("seats")

        # Build dynamic query based on user input
        query = Flight.query

        if destination:
            query = query.filter(Flight.destination.ilike(f"%{destination}%"))
        if travel_date:
            query = query.filter(Flight.departure_time >= travel_date)
        if seats:
            query = query.filter(Flight.total_seats >= int(seats))

        # Execute query
        flights = query.all()

    return render_template("search.html", flights=flights, destinations=destinations)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    signup_form = SignUpForm()

    if login_form.validate_on_submit() and login_form.submit.data:
        # Login logic
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, login_form.password.data):
            # Save user ID and role in session
            session["user_id"] = user.id
            session["user_role"] = user.role
            flash(f"Welcome, {user.first_name}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")

    if signup_form.validate_on_submit() and signup_form.submit.data:
        # Sign-up logic
        existing_user = User.query.filter_by(email=signup_form.email.data).first()
        if existing_user:
            flash("Email already registered.", "warning")
        else:
            hashed_password = bcrypt.generate_password_hash(signup_form.password.data).decode("utf-8")
            new_user = User(
                first_name=signup_form.first_name.data,
                last_name=signup_form.last_name.data,
                email=signup_form.email.data,
                password_hash=hashed_password,
                role="user"
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("login.html", login_form=login_form, signup_form=signup_form)

@app.route("/book/<int:flight_id>", methods=["GET", "POST"])
def book_flight(flight_id):
    # Check if the user is logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to book a flight.", "warning")
        return redirect(url_for("login"))

    # Fetch flight details
    flight = Flight.query.get_or_404(flight_id)

    # Calculate flight duration in hours
    flight_duration = (flight.arrival_time - flight.departure_time).total_seconds() / 3600
    price_per_seat = round(flight_duration * 100, 2)

    if request.method == "POST":
        # Retrieve the number of seats from the form
        seats_requested = request.form.get("seats")

        if not seats_requested or not seats_requested.isdigit():
            flash("Please enter a valid number of seats.", "error")
            return render_template(
                "book.html", logged_in=True, flight=flight, price_per_seat=price_per_seat
            )

        seats_requested = int(seats_requested)
        if seats_requested > flight.total_seats:
            flash("Not enough seats available.", "error")
            return render_template(
                "book.html", logged_in=True, flight=flight, price_per_seat=price_per_seat
            )

        # Create the booking
        new_booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            booking_date=datetime.utcnow(),
            status="CONFIRMED",
            seats=seats_requested,
        )
        db.session.add(new_booking)

        # Update available seats in the flight
        flight.total_seats -= seats_requested
        db.session.commit()

        total_price = seats_requested * price_per_seat
        flash(f"Booking confirmed! Total price: ${total_price}", "success")
        return redirect(url_for("search_flights"))

    return render_template(
        "book.html", logged_in=True, flight=flight, price_per_seat=price_per_seat
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Check if the user is logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for("login"))

    # Fetch user details
    user = db.session.get(User, user_id)

    # Handle booking cancellation
    if request.method == "POST":
        booking_id = request.form.get("booking_id")
        if booking_id:
            booking = Booking.query.get_or_404(booking_id)
            
            # Ensure the booking belongs to the logged-in user
            if booking.user_id != user_id:
                flash("Unauthorized access.", "danger")
                return redirect(url_for("profile"))
            
            # Update flight seats
            flight = Flight.query.get(booking.flight_id)
            flight.total_seats += booking.seats

            # Delete the booking
            db.session.delete(booking)
            db.session.commit()

            flash("Your booking has been canceled.", "info")
            return redirect(url_for("profile"))

    # Query for bookings
    past_bookings = (
        Booking.query.join(Flight)
        .filter(Booking.user_id == user_id, Flight.departure_time < datetime.utcnow())
        .all()
    )
    upcoming_bookings = (
        Booking.query.join(Flight)
        .filter(Booking.user_id == user_id, Flight.departure_time >= datetime.utcnow())
        .all()
    )

    return render_template(
        "profile.html",
        user=user,
        past_bookings=past_bookings,
        upcoming_bookings=upcoming_bookings,
    )

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        user = db.session.get(User, user_id)
        if not user or user.role != "admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    # Fetch all flights and bookings
    flights = Flight.query.all()
    bookings = Booking.query.all()

    if request.method == "POST":
        # Handle booking cancellation
        booking_id = request.form.get("booking_id")
        if booking_id:
            booking = Booking.query.get_or_404(booking_id)
            # Update flight's available seats
            flight = Flight.query.get(booking.flight_id)
            flight.total_seats += booking.seats

            # Delete the booking
            db.session.delete(booking)
            db.session.commit()
            flash(f"Booking {booking_id} has been canceled.", "info")
            return redirect(url_for("admin_dashboard"))

    return render_template("admin.html", flights=flights, bookings=bookings)

@app.route("/logout")
def logout():
    session.clear()  # Clears all session data
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/clear-session")
def clear_session():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
