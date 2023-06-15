from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.widgets import TextArea

from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username занят')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким email зарегистрирован')

    def validate_password(self, password):
        if len(password.data) < 2:
            raise ValidationError('Пароль должен быть не короче 2 символов')



class EditProfileForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    avatar = FileField('Выбрать Файл', validators=[FileAllowed(['jpg', 'png'])])
    about_me = TextAreaField('О себе', widget=TextArea(), validators=[Length(min=0, max=140)])
    submit = SubmitField('Обновить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args,**kwargs)
        self.original_username = original_username


    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username занят')