import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, url_for
#from functools import wraps


""" def login_required(f):
    
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            #changed from login page to index 
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function """


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
