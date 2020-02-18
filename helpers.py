import os
import requests
import urllib.parse

from flask import Flask, redirect, render_template, request, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
#from application import username

# Configure application
app = Flask(__name__)

# calls SQLAlchemy database
db = SQLAlchemy(app)

# defines table values
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    cash = db.Column(db.Float(7), nullable=False)
    remainder = db.Column(db.Float(7), nullable=False) 

"""
@app.route("/register", methods=["POST"])
def login_required(f):
    Register user

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # retrieve user entered information
        username = request.form.get("username")

        # Query database for username
        user = User.query.filter_by(username=username).first()

        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            #calls current user
            
            if session.get("user_id") is not user:
                #changed from login page to index 
                return redirect("/index")
            return f(*args, **kwargs)
        return decorated_function

"""
def login_required(f):
    
    """

    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators

    """
    
    
    @wraps(f)
    def decorated_function(*args, **kwargs):

        #calls current user
        #retrieve user entered information

        if session.get("user_id") is False:
            #changed from login page to index 
            return redirect("/index")
        return f(*args, **kwargs)
    return decorated_function


# allows user to call stocks based on symbol
def lookup(symbol):
    """Look up quote for symbol."""
    os.system("export API_KEY="+"pk_0d1467f2aeb748d0b81f445f22bd6665")

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
