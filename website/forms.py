from wtforms import StringField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import SelectField, FileField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.validators import InputRequired


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=40)])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password', message='passwords must match')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=40)])
    submit = SubmitField('Log in')


class UploadForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['csv'], "CSV files only!")
    ])
    data_type = SelectField("Type of Data",
                       choices=[('gr', 'GoodReads'), ('sg', 'StoryGraph')],
                       validators=[InputRequired()])
    submit = SubmitField('Upload')
