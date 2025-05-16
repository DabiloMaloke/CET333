import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask_login import login_required

app = Flask(__name__)

# Function to get all admins
def get_all_admins():
    conn = sqlite3.connect("database/admins.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM admins")
    admins = cursor.fetchall()
    conn.close()
    return admins

# Add new admin
@app.route('/add_admin', methods=['POST'])
@login_required
def add_admin():
    username = request.form['username']
    password = request.form['password']

    if username and password:
        conn = sqlite3.connect("database/admins.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", 
                       (username, generate_password_hash(password)))
        conn.commit()
        conn.close()
        flash("New admin added successfully!", "success")
    else:
        flash("Please provide both username and password!", "error")

    return redirect(url_for('manage_admins'))

# Delete an admin
@app.route('/delete_admin/<int:admin_id>', methods=['POST'])
@login_required
def delete_admin(admin_id):
    conn = sqlite3.connect("database/admins.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
    conn.commit()
    conn.close()
    flash("Admin deleted successfully!", "success")

    return redirect(url_for('manage_admins'))

# Admin Management Page
@app.route('/manage_admins')
@login_required
def manage_admins():
    admins = get_all_admins()
    return render_template('manage_admins.html', admins=admins)
 
