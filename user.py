from flask_login import UserMixin

class WolUser(UserMixin):

    def __init__(self, username : str, password : str):
        super()
        self.username = username
        self.password = password
        self.id = 1

    jan = None
    @staticmethod
    def getUser(username : str, password : str):
        print("finding {}:{}".format(username, password))
        if username == "jan" and password == "esther":
            WolUser.jan = WolUser("jan", "esther")
            return WolUser.jan
        else:
            return None

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
        return WolUser.jan