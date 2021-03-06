from flask_login import UserMixin

class WolUser(UserMixin):

    users = {}

    def __init__(self, id : int, username : str, admin: bool):
        super()
        self.username = username
        self.id = id
        self.users[id] = self
        self.is_admin = bool(admin)

    @property
    def is_anonymous(self):
        return super().is_anonymous

    def get_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return super().is_authenticated

    @property
    def is_active(self):
        return super().is_active

    @classmethod
    def get(cls, user_id):
        print("users: {}, id: {}".format(cls.users, user_id))
        return cls.users[user_id]

    def __repr__(self):
        return "<WolUser {}, auth:{}, active:{}, anon:{}".format(
            self.get_id(),
            self.is_authenticated,
            self.is_active,
            self.is_anonymous)

from wtforms import Form, PasswordField, validators
class updatePasswordForm(Form):
    old_pw = PasswordField("old_pw", [validators.DataRequired()])
    new_pw = PasswordField("new_pw", [validators.DataRequired()])
