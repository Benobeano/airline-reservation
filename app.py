from flask import Flask, render_template
from models import db
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


app.config['SECRET_KEY'] = 'a-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airline.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search():
    return "Flight Search Page "

@app.route("/login")
def login():
    return "Login / Sign Up Page "


@app.route("/profile")
def profile():
    return "Customer Profile Page"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
