from ast import Pass
from operator import le, length_hint
from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SearchField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from dict.models import User

class SearchForm(FlaskForm):
    searched = StringField(label='Searched', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username = username_to_check.data).first()
        if user:
            raise ValidationError('Username exists!')
        
    def validate_email_address(self, email_address_to_check):
        email= User.query.filter_by(email_address = email_address_to_check.data).first()
        if email:
            raise ValidationError('Email exists!')
            
    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email_address= StringField(label='Email', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Password2', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')
    
class BookmarkForm(FlaskForm):
    submit = SubmitField(label='Bookmark')

    