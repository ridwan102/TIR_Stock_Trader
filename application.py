import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, lookup, usd

# Configure application
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    stockname = db.Column(db.String(80), unique=True, nullable=False)
    stocksymbol = db.Column(db.String(80), unique=True, nullable=False)
    stockprice = db.Column(db.Integer, nullable=False)
    stockshares = db.Column(db.Integer, nullable=False)
    #totalstock = db.Column(db.Integer, nullable=False)

    def __init__(self, username, stockname, stocksymbol, stockshares, stockprice):#, totalstock):
        self.username = username
        self.stockname = stockname
        self.stocksymbol = stocksymbol
        self.stockprice = stockprice
        self.stockshares = stockshares
        #self.totalstock = totalstock

class History(db.Model):
    datetime = db.Column(db.DateTime(), primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    buysell = db.Column(db.String(4), nullable=False)
    stockname = db.Column(db.String(80), nullable=False)
    stocksymbol = db.Column(db.String(80), nullable=False)
    stockprice = db.Column(db.Integer, nullable=False)
    stockshares = db.Column(db.Integer, nullable=False)

    def __init__(self, datetime, username, buysell, stockname, stocksymbol, stockshares, stockprice):
        self.datetime = datetime
        self.username = username
        self.buysell = buysell
        self.stockname = stockname
        self.stocksymbol = stocksymbol
        self.stockprice = stockprice
        self.stockshares = stockshares

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

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # users = User.query.order_by(User.id).all()
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

        # Ensure confirmation password was submitted
        elif not confirmation:
            flash("Please confirm password")
            return redirect("/register")

        # Ensure passwords match
        elif password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        elif user:
            flash("Username is already taken")
            return redirect("/register")

        # saves password to hash
        password = generate_password_hash(password)

        new_user = User(username,password)
        db.session.add(new_user)
        db.session.commit()

        # Save user id into session
        session["user_id"] = User.query.filter_by(username=username).first()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Please provide username")
            return redirect("/login")

        # Ensure password was submitted
        elif not password:
            flash("Please provide password")
            return redirect("/login")

        user = User.query.filter_by(username=username).first()

        # Ensure username exists and password is correct
        if not user:
            flash("Invalid username")
            return redirect("/login")

        if not check_password_hash(user.password, password):
            flash("Invalid password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = user.username

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # calls current user
    username = session["user_id"]

    # deletes rows with no stocks
    # db.execute("DELETE FROM buy WHERE shares = 0")
    Transactions.query.filter_by(username=username, stockshares=0).delete(synchronize_session=False)

    """
    # updates total in dollar value amount of bought stocks
    db.execute("UPDATE buy SET total=price*shares")

    # initializes buy table for current user
    stocks = db.execute("SELECT * FROM buy WHERE user = :user", user=user)

    # totals all stock investments for current user
    stock_total = db.execute("SELECT SUM(total) FROM buy WHERE user = :user", user=user)

    # calls amount of cash user currently has on hand
    cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])

    # check for new users that do not have any investments or else there is an error
    if not stock_total[0]['SUM(total)']:
        stock_totals = 0
    else:
        stock_totals = stock_total[0]['SUM(total)']

    # calculators remainder amount of cash
    remainder = cash[0]['cash'] - stock_totals

    # updates remainder amount of cash
    db.execute("UPDATE users SET remainder = :remainder WHERE username=:username", remainder=remainder, username=user)

    # calculats total of remainder and total investments
    total = remainder + stock_totals

    """
    return render_template("index.html") #, stocks=stocks, stock_totals=stock_totals, remainder=remainder, total=total)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":
        symbol = lookup(request.form.get("symbol"))

        if not symbol:
            flash("Does not exist")
            return redirect("/quote")

        flash(f"{symbol['name']} is ${symbol['price']} per share")
        return redirect("/quote")

    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

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

        if shares <= 0:
            flash("Please enter a number greater than 0")
            return redirect("/buy")

        # calls remainder cash on account
        # remainder = db.execute("SELECT remainder FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["remainder"]

        # calls current price of stock
        price = symbol["price"]

        # if desired total to be bought is greater than remaining cash, flashes error message
        # if price * shares > remainder:
        #    flash("Not enough funds available")
        #    return redirect("/buy")

        # calls current user
        username = session["user_id"]

        # calls amount of current of shares for user
        usershares = Transactions.query.filter_by(username=username,stocksymbol=symbol["symbol"]).first()

        # if the current stock is not in the users profile, it inserts it or else it updates the table
        if not usershares:
            transactions = Transactions(username=username, stockname=symbol["name"], stocksymbol=symbol["symbol"], stockprice=price, stockshares=shares)
            db.session.add(transactions)
            db.session.commit()
        else:
            usershares.stockshares += shares
            db.session.commit()

        # inserts transaction into history
        db.session.add(History(datetime=datetime.now().isoformat(timespec='milliseconds'), username=username,
        buysell='Buy', stockname=symbol["name"], stocksymbol=symbol["symbol"], stockprice=price, stockshares=shares))
        db.session.commit()

        flash(f"Purchased {shares} shares of {symbol['name']}")

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # initializes to current user
    # user = db.execute("SELECT username FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["username"]
    username = session["user_id"]

    # initializes symbol for buy table for current user
    # symbols = db.execute("SELECT symbol FROM buy WHERE user = :user", user=user)
    stocksymbol = db.session.query(Transactions.stocksymbol)#.filter_by(username=username)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        """
        # initializes symbol for buy table for current user
        symbol = symbols[0]["symbol"]

        # if share value to sell is not entered or shares are equal or less than 0, returns apology
        try:
            shares = int(request.form.get("shares"))
        except:
            flash("Please enter a valid amount of shares to sell")
            return redirect("/sell")

        if shares <= 0:
            flash("Please enter a valid amount of shares to sell")
            return redirect("/sell")

        # calls total shares for current user and stock
        total_shares = db.execute("SELECT shares FROM buy WHERE user=:user AND symbol = :symbol",
                                  user=user, symbol=symbol)[0]["shares"]

        # if shares requested to sell is greater than total shares, returns error
        if shares > total_shares:
            flash("Not enough shares")
            return redirect("/sell")

        # looks up stock price based on symbol
        price = lookup(symbol)["price"]

        # calls current stock
        stock = db.execute("SELECT stock FROM buy WHERE user=:user AND symbol = :symbol", user=user, symbol=symbol)[0]["stock"]

        # updates shares for selected stock
        db.execute("UPDATE buy SET shares = shares - :shares WHERE user=:user AND symbol = :symbol", shares=shares, user=user,
                   symbol=symbol)

        # add transaction to history
        db.execute("INSERT INTO history (user, buysell, stock, price, shares) VALUES(:user, 'Sell', :stock, :price, :shares)",
                   user=user, stock=stock, price=price, shares=shares)

        flash(f"Sold {shares} shares of {stock}")

        return redirect("/")
        """

    else:

        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("sell.html", stocksymbol=stocksymbol)


@app.route("/history")
@login_required
def history():

    # calls current user
    username = session["user_id"]

    # initializes history table for current user
    history = History.query.filter_by(username=username)

    return render_template("history.html", history=history)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return (e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
