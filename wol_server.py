from flask import Flask, render_template, request, abort, redirect, url_for, g, flash
import subprocess
import wakeonlan
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import os
from login_form import LoginForm
from user import WolUser, updatePasswordForm
from util import is_safe_url
from urllib.request import Request
from data import DataLayer



data_layer = DataLayer()

app = Flask(__name__)
app.secret_key = os.urandom(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = url_for("login")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    next = request.args.get('next')
    if request.method == "POST":
        if form.validate():
            user = data_layer.getUser(form.username.data, form.password.data)

            if not user:
                print("user does not exist")
                return abort(400)
            user = WolUser(user[0], user[1], user[2])
            login_user(user)
            if not is_safe_url(next):
                print("unsafe redirect")
                return abort(400)
            print("redirecting to {}".format(next or url_for("index")))
            return redirect(next or url_for("index"))
        else:
            print("invalid form")
            return abort(400)
    return render_template("login.html", form=form, next=next)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(user_id):
    if user_id:
        user = WolUser.get(user_id)
        return user
    return None

@app.route("/wake", methods=["POST"])
@login_required
def wake():
    data = request.form["mac"]
    print("wake got {}".format(data))

    data_layer.addMac(current_user.id, data)
    wakeonlan.send_magic_packet(data)


@app.route("/arp")
@login_required
def arp():
    interfaces = data_layer.get_arp()
    user_macs = data_layer.getMacs(current_user.id)
    return render_template("arp.html", data=interfaces, macs=user_macs)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings/main.html")


def get_setting_args(page):
    args = {"change_pw":{"form": updatePasswordForm()}}
    return args[page]


@app.route("/settings/<page>")
@login_required
def setting_content(page):
    args = get_setting_args(page)
    return render_template("settings/{}.html".format(page), **args)


@app.route("/settings/change_pw", methods=["POST"])
@login_required
def update_password():
    form = updatePasswordForm(request.form)
    if form.validate():
        if data_layer.validate_password(current_user.username, form.old_pw.data):
            data_layer.updateUserPassword(current_user.id, form.new_pw.data)
            flash("Password succesfully changed!")
            redirect(url_for("/settings"))
        else:
            abort(400)

@app.route("/credits")
def credits():
    return render_template("credits.html")







