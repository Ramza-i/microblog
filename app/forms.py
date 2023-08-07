from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.widgets import TextArea

from app.models import User


class EditProfileForm(FlaskForm):

    username = StringField('Логин', validators=[DataRequired()])
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
                raise ValidationError('Логин занят')

class PostForm(FlaskForm):
    post = TextAreaField('Скажите что-то', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Отправить')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')