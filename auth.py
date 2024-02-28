import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


# @bp.before_app_request
# def load_logged_in_user():
#     """If a user id is stored in the session, load the user object from
#     the database into ``g.user``."""
#     user_id = session.get("user_id")

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = (
#             get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
#         )


# @bp.route("/register", methods=("GET", "POST"))
# def register():
#     """Register a new user.

#     Validates that the username is not already taken. Hashes the
#     password for security.
#     """
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         db = get_db()
#         error = None

#         if not username:
#             error = "Username is required."
#         elif not password:
#             error = "Password is required."

#         if error is None:
#             try:
#                 db.execute(
#                     "INSERT INTO user (username, password) VALUES (?, ?)",
#                     (username, generate_password_hash(password)),
#                 )
#                 db.commit()
#             except db.IntegrityError:
#                 # The username was already taken, which caused the
#                 # commit to fail. Show a validation error.
#                 error = f"User {username} is already registered."
#             else:
#                 # Success, go to the login page.
#                 return redirect(url_for("auth.login"))

#         flash(error)

#     return render_template("auth/register.html")


# @bp.route("/login", methods=("GET", "POST"))
# def login():
#     """Log in a registered user by adding the user id to the session."""
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         db = get_db()
#         error = None
#         user = db.execute(
#             "SELECT * FROM user WHERE username = ?", (username,)
#         ).fetchone()

#         if user is None:
#             error = "Incorrect username."
#         elif not check_password_hash(user["password"], password):
#             error = "Incorrect password."

#         if error is None:

#             # store the user id in a new session and return to the index
#             session.clear()
#             session["user_id"] = user["id"]
#             return redirect(url_for("index"))


#         flash(error)

#     return render_template("auth/login.html")


# @bp.route("/logout")
# def logout():
#     """Clear the current session, including the stored user id."""
#     session.clear()
#     return redirect(url_for("index"))

# @bp.route("/credit_card", methods=("GET", "POST"))
# def credit_card():
#     if request.method == "POST":
#         card_number = request.form.get('card_number')
#         expiration_date = request.form.get('expiration_date')
#         security_code = request.form.get('security_code')
#         error = None
#         db = get_db()
#         user_id = session.get("user_id")

#         if user_id is None:
#             g.user = None
#         else:
#             g.user = (
#                 get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
#             )
        
#         if not (card_number and expiration_date and security_code):
#             error = "Credit card is required."
            
#         if error is None:
#             try:
                
#                 db.execute(
#                     "INSERT INTO credit_card (user_id, card_number, expiration_date, security_code) VALUES (?, ?, ?, ?)",
#                     (g.user["id"], card_number, expiration_date, security_code),
#                 )
#                 db.commit()
#                 return redirect(url_for("index"))
#             except db.IntegrityError:
#                 # The username was already taken, which caused the
#                 # commit to fail. Show a validation error.
#                 error = f"Failed to save credit card information for user {g.user["id"]}."
#         else:
#             render_template("auth/credit_card.html")
#     return render_template("auth/credit_card.html")


# @bp.route("/payment", methods=("GET", "POST"))
# def payment():
#     if request.method == "POST":
#         return redirect(url_for("index"))
#     db = get_db()

#     post  = db.execute(
#         "SELECT * FROM credit_card WHERE user_id = ?", (g.user["id"],)
#     ).fetchone()

#     if post is not None:

#         # 投稿の本文に "sold out" を追加します
#         card_number = post['card_number'] 
#         expiration_date = post['expiration_date']
#         security_code = post['security_code'] 
        
#     return render_template("auth/payment.html", card_number=card_number, expiration_date=expiration_date, security_code=security_code)

