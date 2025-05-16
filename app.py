import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from werkzeug.security import check_password_hash
import subprocess
import os
from datetime import datetime

# Database setup (if needed)
def setup_database():
    conn = sqlite3.connect('database/admin.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# User authentication functions
def get_admin(username):
    conn = sqlite3.connect("database/admin.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = cursor.fetchone()
    conn.close()
    return admin

def verify_login(username, password):
    admin = get_admin(username)
    if admin and check_password_hash(admin[2], password):
        return True
    return False

# Data fetching function
def fetch_data_for_dashboard():
    try:
        logs = pd.read_csv('synthetic_logs.csv')
        
        total_requests = len(logs)
        unique_visitors = logs["IP Address"].nunique()
        
        status_counts = logs["Status Code"].value_counts().to_dict()
        endpoint_counts = logs["Endpoint"].value_counts().head(5).to_dict()

        return {
            "total_requests": total_requests,
            "unique_visitors": unique_visitors,
            "status_counts": status_counts,
            "top_endpoints": endpoint_counts,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Login page
def login_page():
    st.title("Admin Dashboard Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if verify_login(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Dashboard page
def dashboard_page():
    st.title("Web Analytics Dashboard")
    
    # Logout button
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.experimental_rerun()
    
    st.write(f"Welcome, {st.session_state['username']}!")
    
    data = fetch_data_for_dashboard()
    if not data:
        return
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Requests", data['total_requests'])
    with col2:
        st.metric("Unique Visitors", data['unique_visitors'])
    
    st.write(f"Last updated: {data['last_updated']}")
    
    # Status code distribution chart
    st.subheader("Status Code Distribution")
    status_fig = go.Figure([go.Bar(
        x=list(data["status_counts"].keys()),  
        y=list(data["status_counts"].values()),
        marker_color="blue"
    )])
    st.plotly_chart(status_fig)
    
    # Top endpoints pie chart
    st.subheader("Top 5 Endpoints")
    endpoint_fig = go.Figure([go.Pie(
        labels=list(data["top_endpoints"].keys()),
        values=list(data["top_endpoints"].values())
    ])
    st.plotly_chart(endpoint_fig)

# Main app logic
def main():
    setup_database()
    
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if st.session_state['authenticated']:
        dashboard_page()
    else:
        login_page()

if __name__ == "__main__":
    # Start background processes if needed
    # subprocess.Popen(["python", "data_generator.py"])
    main()
