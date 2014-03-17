from flask.ext.wtf import Form
# from wtforms.fields import TextField, TextAreaField, PasswordField, StringField
# from wtforms.validators import Required, EqualTo

from wtforms import TextField, TextAreaField, PasswordField, validators

class RegistrationForm(Form):
    username = TextField("Username", [validators.Required()])
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required(),
    									  validators.EqualTo("confirm", message="Your passwords do not match.")])
    confirm = PasswordField("Re-enter Password")

class LoginForm(Form):
	email = TextField("Email", [validators.Required(), validators.Email()])
	password = PasswordField("Password", [validators.Required()])
