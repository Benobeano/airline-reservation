from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class SignUpForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=3),
        EqualTo("confirm_password", message="Passwords must match")
    ])
    confirm_password = PasswordField("Confirm Password")
    submit = SubmitField("Sign Up")
