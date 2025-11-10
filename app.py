# from email_validator import EmailNotValidError, validate_email


import base64
import hashlib
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# import imageOCR
import passCheck as passc
from dailymed_fetch import get_xml, parse_xml
from emailValidation import EmailValidator
from flask_session import Session
from medicine_identifier import MedicineIdentifier

load_dotenv()

dbUser = os.getenv("dbUser")
dbPass = os.getenv("dbPassword")
dbURL = os.getenv("dbURL")

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.secret_key = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{dbUser}:{dbPass}@{dbURL}"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)


class UserHistory(db.Model):
    email = db.Column(db.String(100), nullable=False)
    setid = db.Column(db.String(100), primary_key=True)
    medName = db.Column(db.String(200), nullable=False)


def createSession(email):
    userData = UserInfo.query.filter_by(email=email).first()
    session.update({"user_id": userData.id, "user_email": userData.email})
    return True


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
            createSession(user.email)
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
        createSession(email)
        return redirect(url_for("home"))
    return render_template("register.html")


@app.route("/search")
def home():
    if "user_email" in session:
        return render_template("search.html")
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template("about.html", title="MedOCR-About")


@app.route("/medicine/<set_id>")
def medicine(set_id):
    xml_response = get_xml(set_id)
    med_name, setid, form, route, sections = parse_xml(xml_response)
    return render_template("medicine.html", sections=sections)


@app.route("/history")
def history():
    if "user_email" in session:
        email = session["user_email"]
        # Get user's search history, ordered by most recent first
        history_entries = (
            UserHistory.query.filter_by(email=email)
            .order_by(UserHistory.setid.desc())
            .all()
        )
        print(f"Found {len(history_entries)} history entries")  # Debug print

        return render_template(
            "history.html", history=history_entries, title="Search History"
        )
    else:
        return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if "user_email" in session:
        return render_template("profile.html")
    else:
        return redirect(url_for("login"))


@app.route("/uploadImage", methods=["POST"])
def upload():
    data = request.get_json()
    imageData = data["image"]
    encodedData = imageData.split(",")[1]
    imgBytes = base64.b64decode(encodedData)
    csvPath = "samples/meds-main.csv"
    identifier = MedicineIdentifier(csvPath)
    result = identifier.identify_medicine(imgBytes, top_matches=5)
    topResult = result["matches"][0]["setid"]
    if topResult:
        topName = result["matches"][0]["description"]
        email = session.get("user_email")
        newHistory = UserHistory(email=email, setid=topResult, medName=topName)
        db.session.add(newHistory)
        db.session.commit()
        return jsonify({"setid": topResult})


if __name__ == "__main__":
    app.run(
        debug=False,
    )
