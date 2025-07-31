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
    name = StringField('Name', validators=[DataRequired(),Length(min=8, max=40)])
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

class EmailForm(FlaskForm):
    new_email = StringField('New Email', validators=[DataRequired(), Email()])
    confirm = StringField('Confirm Email', validators=[DataRequired(), Email(),EqualTo('new_email',message='emails must match')])

    password = PasswordField('Password',validators=[DataRequired(),Length(min=8, max=40)])
    submit = SubmitField('Update Email')


class PasswordForm(FlaskForm):
    old_password = PasswordField('Old Password',validators=[DataRequired(),Length(min=8, max=40)])
    new_password = PasswordField('New Password',validators=[DataRequired(),Length(min=8, max=40)])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('new_password', message='passwords must match')])
    submit = SubmitField('Update Password')



class NameForm(FlaskForm):
    new_name = StringField('Name', validators=[DataRequired(),Length(min=1, max=40)])
    submit = SubmitField('Update Name')


