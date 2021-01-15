import os
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gym.db")

#######################################################  INDEX  #########################################################

@app.route("/")
@login_required
def index():
    """Show details of user"""
    tips = []
    tips.append("Periodic fasting can help clear up the mind and strengthen the body and the spirit.")
    tips.append("When you fast, insulin levels drop and human growth hormone increases. Your cells also initiate important cellular repair processes and change which genes they express.")
    tips.append("Intermittent fasting helps you eat fewer calories, while boosting metabolism slightly. It is a very effective tool to lose weight and belly fat.")
    tips.append("Intermittent fasting can reduce insulin resistance and lower blood sugar levels, at least in men.")
    tips.append("Intermittent fasting can reduce oxidative damage and inflammation in the body. This should have benefits against aging and development of numerous diseases.")
    tips.append("Intermittent fasting can improve numerous risk factors for heart disease such as blood pressure, cholesterol levels, triglycerides and inflammatory markers.")
    tips.append("Fasting triggers a metabolic pathway called autophagy, which removes waste material from cells.")
    tips.append("Intermittent fasting has been shown to help prevent cancer in animal studies. One paper in humans showed that it can reduce side effects caused by chemotherapy.")
    tips.append("Intermittent fasting may have important benefits for brain health. It may increase growth of new neurons and protect the brain from damage.")
    tips.append("Studies in animals suggest that intermittent fasting may be protective against neurodegenerative diseases like Alzheimer's disease.")
    rnd = random.randint(0,9)

    details = db.execute("SELECT * FROM details WHERE id = ?", session["user_id"])
    return render_template("index.html",tip = tips[rnd], details = details)

#######################################################  REGISTER  #########################################################

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Ensure username was submitted
    if request.method == "POST":

        pass_hash = generate_password_hash(request.form.get("password"))
        first = request.form.get("first")
        last = request.form.get("last")
        email = request.form.get("email")
        phone = request.form.get("phone")
        age = request.form.get("age")
        length = request.form.get("length")
        weight = request.form.get("weight")
        goal_weight = request.form.get("goal_weight")
        months = int(request.form.get("months"))
        emails = db.execute("SELECT * FROM users WHERE email = ?", email)
        ### DATA CHECKING ###
        # Ensure name was typed correctly
        if not first or not last:
            return apology("Must Provide Fullname")

        # Ensure email was submitted
        elif not email:
            return apology("Must Provide Email")

        # Ensure email is not existed

        #### MARIAM T3MLO ####
        elif len(emails) == 1:
            return apology("Already Registered")

        # Ensure phone was submitted
        elif not phone:
            return apology("Must Provide Phone")

        # Ensure age was submitted
        elif not age:
            return apology("Must Provide Age")

        # Ensure length was submitted
        elif not length:
            return apology("Must Provide Length")

        # Ensure weight was submitted
        elif not weight or not goal_weight:
            return apology("Must Provide Weight")

        # Ensure months was submitted
        elif not months:
            return apology("Must Provide Wonths")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must Provide Password")

        # Ensure confirm was submitted
        elif not request.form.get("confirmation"):
            return apology("Must Confirm Password")

        # Ensure two passwords match
        elif not check_password_hash(pass_hash, request.form.get("confirmation")):
            return apology("Passwords Don't Match")

        # Checking Sickness
        sick = "no"
        if request.form.get("is_sick") == "yes":
            sick = "yes"

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    db.execute("INSERT INTO users (first, last, phone, email, hash) VALUES(?, ?, ?, ?, ?)",
                (first, last, phone, email, pass_hash))

    db.execute("INSERT INTO details (age, weight, goal_weight, length, is_sick, months) VALUES (?, ?, ?, ?, ?, ?)",
                (age, weight, goal_weight, length, sick, months))

    start = db.execute("SELECT start FROM details WHERE id = (SELECT id FROM users WHERE email = ?)", email)[0]["start"]

    if months == 1:
        db.execute("UPDATE details SET end = (select date(start, '+1 month')) WHERE id = (SELECT id FROM users WHERE email = ?)", email)
    elif months == 3:
        db.execute("UPDATE details SET end = (select date(start, '+3 month')) WHERE id = (SELECT id FROM users WHERE email = ?)", email)
    elif months == 6:
        db.execute("UPDATE details SET end = (select date(start, '+6 month')) WHERE id = (SELECT id FROM users WHERE email = ?)", email)
    elif months == 12:
        db.execute("UPDATE details SET end = (select date(start, '+1 years')) WHERE id = (SELECT id FROM users WHERE email = ?)", email)
    elif months == 24:
        db.execute("UPDATE details SET end = (select date(start, '+2 years')) WHERE id = (SELECT id FROM users WHERE email = ?)", email)

    return render_template("registered.html")


 #######################################################  LOGIN  #########################################################

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("Must Provide Email")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must Provide Password")

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email = request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid Email Or Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

#######################################################  LOGOUT  #########################################################

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

#######################################################  ABOUT  #########################################################

@app.route("/about")

def about():
    """about gym"""
    return render_template("about.html")


#######################################################  LOCATION  #########################################################

@app.route("/location")

def location():
    """Show location"""
    return render_template("location.html")

#######################################################  EXERCISES  #########################################################

@app.route("/exercises")
@login_required
def exercises():
    """show exercises"""
    return render_template("exercises.html")



#######################################################  DIET  #########################################################

@app.route("/diet")
@login_required
def diet():
    """show diet"""
    return render_template("diet.html")


#####################################################  UPDATE DATA  #####################################################
@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """update data"""
    if request.method == "POST":
        phone = request.form.get("phone")
        age = request.form.get("age")
        length = request.form.get("length")
        weight = request.form.get("weight")
        goal_weight = request.form.get("goal_weight")
        months = request.form.get("months")
        sick = request.form.get("is_sick")


        # Ensure age was submitted
        if not age and not length and not weight and not goal_weight and not months and not phone and not sick:
            return apology("Provide Any Update")
        if age:
            db.execute("UPDATE details SET age = ? WHERE id = ?",(age, session["user_id"]))
        if length:
            db.execute("UPDATE details SET length = ? WHERE id = ?",(length, session["user_id"]))
        if weight:
            db.execute("UPDATE details SET weight = ? WHERE id = ?",(weight, session["user_id"]))
        if goal_weight:
            db.execute("UPDATE details SET goal_weight = ? WHERE id = ?",(goal_weight, session["user_id"]))
        if months:
            db.execute("UPDATE details SET months = ? WHERE id = ?",(months, session["user_id"]))
            #update end
            #now = db.execute(select date('now'))
            db.execute("UPDATE details SET start = (SELECT date('now')) WHERE id = ?", session["user_id"])
            end = db.execute("SELECT start FROM details WHERE id = ?",session["user_id"])[0]["start"]
            if months == 1:
                db.execute("UPDATE details SET end = (select date(end, '+1 month')) WHERE id = ?", session["user_id"])
            elif months == 3:
                db.execute("UPDATE details SET end = (select date(end, '+3 month')) WHERE id = ?", session["user_id"])
            elif months == 6:
                db.execute("UPDATE details SET end = (select date(end, '+6 month')) WHERE id = ?", session["user_id"])
            elif months == 12:
                db.execute("UPDATE details SET end = (select date(end, '+1 years')) WHERE id = ?", session["user_id"])
            elif months == 24:
                db.execute("UPDATE details SET end = (select date(end, '+2 years')) WHERE id = ?", session["user_id"])
        if phone:
            db.execute("UPDATE users SET phone = ? WHERE id = ?" ,(phone, session["user_id"]))
        if sick:
            db.execute("UPDATE details SET is_sick = ? WHERE id = ?",(sick, session["user_id"]))
        return redirect("/")
    else:
        return render_template("update.html")


##########################################################################################################################
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
