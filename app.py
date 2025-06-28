# from email_validator import EmailNotValidError, validate_email


import hashlib

from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

import passCheck as passc
from emailValidation import EmailValidator
from flask_session import Session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://medocr:db-medOCR@localhost/MedOCR"
)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)


@app.route("/")
def homePage():
    return render_template("index.html", title="MedOCR-Search Medicine Info From Image")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["userEmail"]
        password = request.form["userPass"]
        # Validate email
        validity = EmailValidator.validate(email)
        if validity["is_valid"]:
            email = validity["email"]
        else:
            return render_template("login.html", message="Please enter a valid email!")

        pwhash = hashlib.sha256(password.encode()).hexdigest()
        # database query on email
        user = UserInfo.query.filter_by(email=email).first()
        if user and pwhash == user.password:
            session["email"] = user.email
            return redirect(url_for("home"))
        else:
            return render_template(
                "login.html", err_message="Incorrect Email Or Password"
            )

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["userEmail"]
        password = request.form["userPass"]
        # Validate email
        validity = EmailValidator.validate(email)
        if validity["is_valid"]:
            email = validity["email"]
        else:
            return render_template(
                "register.html", err_message="Please enter a valid email!"
            )
        # check password validity and get error message
        pass_valid, msg = passc.validate_password(password)
        if not pass_valid:
            return render_template("register.html", err_message=msg)

        existing_user = UserInfo.query.filter_by(email=email).first()
        if existing_user:
            return render_template(
                "register.html", err_message="Email already registered!"
            )

        hashed = hashlib.sha256(password.encode())
        pwHash = hashed.hexdigest()

        newUser = UserInfo(email=email, password=pwHash)
        db.session.add(newUser)
        db.session.commit()
        # hashed_pw = generate_password_hash(password)
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/home")
def home():
    if "email" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template("about.html", title="MedOCR-About")


if __name__ == "__main__":
    app.run(debug=True)
