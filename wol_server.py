from flask import Flask, render_template, request, abort, redirect, url_for
import subprocess
import wakeonlan
from flask_login import LoginManager, login_required, login_user
import os
from login_form import LoginForm
from user import WolUser
from util import is_safe_url
from pprint import pprint
from urllib.request import Request


app = Flask(__name__)
app.debug=True
app.secret_key = os.urandom(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


@app.route("/")
def index():
    return "hello there again"

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    next = request.args.get('next')
    if request.method == "POST":
        if form.validate():

            user = WolUser.getUser(form.username.data, form.password.data)
            if user == None:
                print("user does not exist")
                return abort(400)
            login_user(user)


            pprint("next: {}".format(next))
            pprint(request.data)
            if not is_safe_url(next):
                print("unsafe redirect")
                return abort(400 )
            print("redirecting to {}".format(next or url_for("index")))
            return redirect(next or url_for("index"))
        else:
            print("invalid form")
            return abort(400)
    return render_template("login.html", form=form, next=next)

@login_manager.user_loader
def load_user(user_id):
    if user_id:
        return WolUser.get(user_id)
    return None

@app.route("/wake", methods=["POST"])
@login_required
def wake():
    print("wake got {}".format(request.data))
    Re
    #wakeonlan.send_magic_packet()

@app.route("/arp")
@login_required
def arp():
    output = subprocess.check_output(["arp", "-a"]).decode().split("\r\n",)
    output = [x for x in output if len(x) != 0]
    rows = [x.split(" ") for x in output]
    for i in range(len(rows)):
        rows[i] = [x for x in rows[i] if len(x) != 0]

    interfaces = []
    interface = None
    for i in range(len(rows)):
        row = rows[i]
        if "Interface" in row[0]:
            interface = {"name": row[1], "entries": []}
            interfaces.append(interface)
        elif row[0][0].isnumeric():
            interface["entries"].append(row)


    return render_template("arp.html", data=interfaces)
