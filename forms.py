from flask.ext.wtf import Form
# from wtforms.fields import TextField, TextAreaField, PasswordField, StringField
# from wtforms.validators import Required, EqualTo

from wtforms import TextField, TextAreaField, PasswordField, validators

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])


    # username = StringField("Username", validators = [Required()])
    # email = StringField("Email", validators = [Required()])
    # password = PasswordField("Password", validators = [Required()])
    #                                       validators.EqualTo("confirm", message="Your passwords do not match.")])
    # confirm = PasswordField("Re-enter Password")

# from wtforms import Form, BooleanField, StringField, validators

# class RegistrationForm(Form):
#     username = StringField("Username", [validators.Length(min=5, max=25)])
#     email = StringField("Email Address", [validators.Length(min=6, max=35)])
#     accept_rules = BooleanField("I accept the site rules", [validators.InputRequired()])