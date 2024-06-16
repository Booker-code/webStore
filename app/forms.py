from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('用戶名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('密碼', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('確認密碼', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('電話號碼')  # 新增電話欄位
    address = StringField('地址')  # 新增地址欄位
    submit = SubmitField('送出')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('密碼', validators=[DataRequired()])
    submit = SubmitField('登入')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('重設密碼')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('新密碼', validators=[DataRequired()])
    password_confirm = PasswordField('確認新密碼', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    email = StringField('Email')
    
class UpdateProfileForm(FlaskForm):
    username = StringField('用戶名', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('密碼', validators=[DataRequired()])
    phone = StringField('電話號碼')  # 新增電話欄位
    address = StringField('地址')  # 新增地址欄位
    submit = SubmitField('Update Profile')