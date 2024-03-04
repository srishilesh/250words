import functools
from flask import Blueprint, request, flash, render_template, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    If GET, display register form
    Get username and password from UI
    Connect to DB
    Validate username and password
    Execute insert query into DB
    If username already exists, throw error
    Else redirect to login page
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered"
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    return render_template('auth/register.html')
        
@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    If GET, display login form
    Get username and password
    Run SQL query to fetch details based on username
    If not found, throw username error
    If password doesn't match, throw password error
    If no error, clear session and set "user_id" with "id", and redirect to index page
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        
        if error is None:
            session.clear()
            session['user_id'] = user["id"]
            return redirect(url_for('index'))
        flash(error)
    
    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    """
    before_app_request - runs before every request is made
    Get session details and set g.user
    If not found, set None
    If found, get user details and assign globally
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM user WHERE id=?", (user_id,)).fetchone()

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    """
    Decorater to wrap original view to check if user is loaded
    Or it redirects to login page to login
    If logged in, loads original view
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view