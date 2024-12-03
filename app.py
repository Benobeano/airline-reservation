from flask import Flask, flash, redirect, render_template, session, url_for
from forms import LoginForm, SignUpForm
from models import User, db
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SECRET_KEY'] = 'a-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airline.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def home():
    user_full_name = None
    if "user_id" in session:
        user = db.session.get(User, session.get("user_id"))
        if user:
            user_full_name = f"{user.first_name} {user.last_name}"
    return render_template("home.html", user_full_name=user_full_name)


@app.route("/search")
def search():
    return "Flight Search Page "



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


@app.route("/profile")
def profile():
    return "Customer Profile Page"

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
