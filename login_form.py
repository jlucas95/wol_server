from wtforms import Form, PasswordField, StringField, validators

class LoginForm(Form):
    username = StringField("username", [validators.DataRequired()])
    password = PasswordField("password", [validators.DataRequired()])