from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import email_validator


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=40)])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password', message='passwords must match')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=40)])
    submit = SubmitField('Log in')
