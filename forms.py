from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,IntegerField,FieldList
from wtforms.validators import length,DataRequired,ValidationError,Length,EqualTo
from models import User


class LoginForm(FlaskForm):
    email = StringField('User Email',validators = [DataRequired()])
    password = PasswordField('Password',validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Length(min=2,max=100)])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=2,max=20)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That user name is already taken. Please take a different one")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is already taken. Please take a different one")