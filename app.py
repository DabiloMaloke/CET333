from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects to login page if user is not authenticated

# Define the User class
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database/admin.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# Function to get admin details
def get_admin(username):
    conn = sqlite3.connect("database/admin.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = cursor.fetchone()
    conn.close()
    return admin

# Root route redirects to login
@app.route("/")
def index():
    if current_user.is_authenticated:
        logout_user()  # Force logout when the user revisits
        session.clear()  # Clear the session data
    return redirect(url_for("login"))

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))  # Redirect if already logged in

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = get_admin(username)

        if admin and check_password_hash(admin[2], password):
            user = User(admin[0], admin[1], admin[2])
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
    
    return render_template("login.html")

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Function to fetch dashboard data
def fetch_data_for_dashboard():
    logs = pd.read_csv('synthetic_logs.csv')

    total_requests = len(logs)
    unique_visitors = logs["IP Address"].nunique()
    
    # Status Code Counts
    status_counts = logs["Status Code"].value_counts().to_dict()
    
    # Top 5 Endpoints by Request Count
    endpoint_counts = logs["Endpoint"].value_counts().head(5).to_dict()

    data = {
        "total_requests": total_requests,
        "unique_visitors": unique_visitors,
        "status_counts": status_counts,
        "top_endpoints": endpoint_counts
    }

    return data

# Dashboard Route
@app.route("/dashboard")
@login_required
def dashboard():
    data = fetch_data_for_dashboard()

    # Bar Chart for Status Code Distribution
    status_fig = go.Figure([go.Bar(
        x=list(data["status_counts"].keys()),  
        y=list(data["status_counts"].values()),
        marker_color="blue"
    )])
    status_chart = status_fig.to_html(full_html=False)

    # Pie Chart for Top 5 Endpoints
    endpoint_fig = go.Figure([go.Pie(
        labels=list(data["top_endpoints"].keys()),
        values=list(data["top_endpoints"].values())
    )])
    endpoint_chart = endpoint_fig.to_html(full_html=False)

    return render_template("dashboard.html", data=data, status_chart=status_chart, endpoint_chart=endpoint_chart)

def start_background_processes():
    # Start data generator
    subprocess.Popen(["python", "data_generator.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)

    # Start Streamlit dashboard
    subprocess.Popen([
        "streamlit", "run", "dashboard.py", "--server.headless", "true"
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == "__main__":
    start_background_processes()
    app.run(debug=True, use_reloader=False)  # Disables auto-reload
