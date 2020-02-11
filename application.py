import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, lookup, usd

# Configure application
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# calls SQLAlchemy database
db = SQLAlchemy(app)

# defines table values
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    cash = db.Column(db.Float(7), nullable=False)
    remainder = db.Column(db.Float(7), nullable=False)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    stockname = db.Column(db.String(80), unique=True, nullable=False)
    stocksymbol = db.Column(db.String(80), unique=True, nullable=False)
    stockprice = db.Column(db.Float(7), nullable=False)
    stockshares = db.Column(db.Integer, nullable=False)
    stocktotal = db.Column(db.Float(7), nullable=False)

class History(db.Model):
    datetime = db.Column(db.DateTime(), primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    buysell = db.Column(db.String(4), nullable=False)
    stockname = db.Column(db.String(80), nullable=False)
    stocksymbol = db.Column(db.String(80), nullable=False)
    stockprice = db.Column(db.Float(7), nullable=False)
    stockshares = db.Column(db.Float(7), nullable=False)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    #set up api key for the stock quote engine
    try:
        os.environ["API_KEY"] = "pk_0d1467f2aeb748d0b81f445f22bd6665"
    except:
        raise RuntimeError("API_KEY not set")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # retrieve user entered information
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Query database for username
        user = User.query.filter_by(username=username).first()

        # Enter valid username
        if not username:
            flash("Please enter a username")
            return redirect("/register")

        # Enter valid password
        elif not password:
            flash("Please enter a password")
            return redirect("/register")

        # Password was not confirmed
        elif not confirmation:
            flash("Please confirm password")
            return redirect("/register")

        # Ensure passwords match
        elif password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        # if username is taken
        elif user:
            flash("Username is already taken")
            return redirect("/register")

        # saves password to hash
        password = generate_password_hash(password)

        # adds username, password, cash available and remainder to table
        db.session.add(User(username=username,password=password,cash=10000,remainder=10000))
        db.session.commit()

        # Save user id into session
        # Do not change to session["user_id"] = user; for some reason website does not run properly 
        session["user_id"] = User.query.filter_by(username=username).first()

        # Redirect user to home page
        return redirect("/index")


@app.route("/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # calls entered username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # finds entered username in database
        user = User.query.filter_by(username=username).first()

        # Ensure username was submitted
        if not username:
            flash("Please provide username")
            return redirect("/")

        # Ensure password was submitted
        elif not password:
            flash("Please provide password")
            return redirect("/")

        # Ensure username exists and password is correct
        elif not user:
            flash("Invalid username")
            return redirect("/")

        elif not check_password_hash(user.password, password):
            flash("Invalid password")
            return redirect("/")

        # Remember which user has logged in
        # Do not change to session["user_id"] = user; for some reason website does not run properly 
        session["user_id"] = User.query.filter_by(username=username).first()

        # Redirect user to home page
        return redirect("/index")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/index")
@login_required
def index():
    """Show portfolio of stocks"""

    session["user_id"] = User.query.filter_by(username=username).first()

    # calls current user
    username = session["user_id"]

    # calls total investments for current user
    total = username.cash

    # calls remaining cash for current user
    remainder = username.remainder

    # tries calling transactions for current user
    try:

        # initializes transactions table for current user
        transactions = Transactions.query.filter_by(username=username.username)

        # totals all stock investments for current user
        stocktotal = transactions.with_entities(func.sum(Transactions.stocktotal).label("total")).first().total

        # calculates remainder amount of cash
        remainder = total - stocktotal

        # updates remainder
        username.remainder = remainder
        db.session.commit()

    # if new user then defaults to this
    except:

        # calculates total stocks invested based on cash total and remainder; for a new user it will always be 0
        stocktotal = total - remainder

    # returns html template
    return render_template("index.html", total=total, remainder=remainder, transactions=transactions, stocktotal=stocktotal)

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        symbol = lookup(request.form.get("symbol"))

        # warning if symbol does not exist
        if not symbol:
            flash("Does not exist")
            return redirect("/quote")

        flash(f"{symbol['name']} is ${symbol['price']} per share")
        return redirect("/quote")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        return render_template("buy.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # calls which stock symbol user input
        symbol = lookup(request.form.get("symbol"))

        # if the user enters an incorrect symbol, they are prompted
        if not symbol:
            flash("Does not exist")
            return redirect("/buy")

        # it initially sees if a valid number of shares is entered
        try:
            shares = int(request.form.get("shares"))
        except:
            flash("Please enter a valid amount of shares to buy")
            return redirect("/buy")

        # warns the user for entering symbol less than zero
        if shares <= 0:
            flash("Please enter a number greater than 0")
            return redirect("/buy")

        # calls current user
        username = session["user_id"]

        # calls remainder cash on account
        remainder = username.remainder

        # calls current price of stock
        price = symbol["price"]

        # if desired total to be bought is greater than remaining cash, flashes error message
        if price * shares > remainder:
            flash("Not enough funds available")
            return redirect("/buy")

        try:

            # calls amount of current of shares for user
            usershares = Transactions.query.filter_by(username=username,stocksymbol=symbol["symbol"]).first()

            # adds that amount of shares to stock
            usershares.stockshares += shares
            usershares.stocktotal = usershares.stockprice*usershares.stockshares
            db.session.commit()

        except:

            # if the current stock is not in the users profile, it inserts it or else it updates the table
            transactions = Transactions(username=username.username, stockname=symbol["name"], stocksymbol=symbol["symbol"],
            stockprice=price, stockshares=shares, stocktotal=price*shares)
            db.session.add(transactions)
            db.session.commit()

        # deducts bought shares and price back to remainder
        username.remainder += shares*price

        # inserts transaction into history
        db.session.add(History(datetime=datetime.now().isoformat(timespec='milliseconds'), username=username.username,
        buysell='Buy', stockname=symbol["name"], stocksymbol=symbol["symbol"], stockprice=price, stockshares=shares))
        db.session.commit()

        flash(f"Purchased {shares} shares of {symbol['name']}")

        return redirect("/index")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # initializes to current user
    username = session["user_id"]

    if request.method == "GET":

        # initializes name for tranactions table for current user
        stocknames = Transactions.query.filter_by(username=username.username, stockname=Transactions.stockname)

        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("sell.html", stockname=stocknames)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # initializes selected stockname for transactions table for current user
        selectedstock = request.form.get("stockname")

        # if share value to sell is not entered or shares are equal or less than 0, returns apology
        try:
            shares = int(request.form.get("shares"))
        except:
            flash("Please enter a valid amount of shares to sell")
            return redirect("/sell")

        # if shares is less than 0 then it flashes warning
        if shares <= 0:
            flash("Please enter a valid amount of shares to sell")
            return redirect("/sell")

        # calls current user and stock info
        stockinfo = Transactions.query.filter_by(username=username.username,stockname=selectedstock).first()

        # if shares requested to sell is greater than total shares, returns error
        if shares > stockinfo.stockshares:
            flash("Not enough shares")
            return redirect("/sell")

        # looks up stock price based on symbol
        price = lookup(stockinfo.stocksymbol)["price"]

        # updates shares for selected stock
        stockinfo.stockshares -= shares
        db.session.commit()

        # updates stocktotal for selected app
        stockinfo.stocktotal = stockinfo.stockprice*stockinfo.stockshares
        db.session.commit()

        # adds sold shares and price back to remainder
        username.remainder += shares*price
        db.session.commit()

        # deletes row if there are no more stockshares in stock
        if stockinfo.stockshares == 0:
            Transactions.query.filter_by(username=username.username, stockname=selectedstock).delete()
            db.session.commit()

        # add transaction to history
        db.session.add(History(datetime=datetime.now().isoformat(timespec='milliseconds'), username=username.username,
        buysell='Sell', stockname=selectedstock, stocksymbol=stockinfo.stocksymbol, stockprice=price, stockshares=shares))
        db.session.commit()

        flash(f"Sold {shares} shares of {selectedstock}")

        return redirect("/index")


@app.route("/history")
@login_required
def history():

    # calls current user
    username = session["user_id"]

    # initializes history table for current user
    history = History.query.filter_by(username=username.username)

    return render_template("history.html", history=history)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return (e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
