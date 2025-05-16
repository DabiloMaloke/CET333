import os
from pathlib import Path
import streamlit as st
import json
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime
from io import StringIO
from werkzeug.security import check_password_hash, generate_password_hash

# ========== CLOUD CONFIG ==========
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "database", "admin.db")
DATA_PATH = os.path.join(BASE_DIR, "sales_dashboard_data.json")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ========== AUTHENTICATION ==========
def init_db():
    """Initialize database with admin credentials"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
    
    # Add default admin if none exists
    if not c.execute("SELECT 1 FROM admins LIMIT 1").fetchone():
        c.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                ("admin", generate_password_hash("admin123")))
    conn.commit()
    conn.close()

def get_admin(username):
    """Retrieve admin from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = c.fetchone()
    conn.close()
    return admin

def login_page():
    """Login page with authentication"""
    st.title("🔒 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        admin = get_admin(username)
        if admin and check_password_hash(admin[2], password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

# ========== DASHBOARD FUNCTIONS ==========
def load_sales_data():
    """Load real-time JSON sales data"""
    try:
        if not os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'w') as f:
                json.dump([], f)
            return []
        
        current_mod_time = os.path.getmtime(DATA_PATH)
        if current_mod_time > st.session_state.get('last_update', 0):
            with open(DATA_PATH, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                st.session_state.last_update = current_mod_time
                return data
        return st.session_state.get('sales_data', [])
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        return []

def get_historical_data():
    """Fetch historical data from SQLite"""
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'sales_data.db'))
        query = "SELECT * FROM sales ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

# ========== DASHBOARD LAYOUT ==========
def sales_dashboard():
    """Main dashboard with real-time analytics"""
    st.set_page_config(page_title="Real-Time Sales Dashboard", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
        :root {
            --primary-color: #00f2ff;
            --secondary-color: #ff00e6;
            --dark-bg: #0a0a1a;
            --card-bg: rgba(20, 20, 40, 0.7);
            --border-color: rgba(0, 242, 255, 0.3);
        }
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            font-family: 'Roboto', sans-serif;
        }
        .stMetric {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 Real-Time Sales Dashboard")
    st.markdown(f"Welcome, {st.session_state['username']} | [Logout](#logout)")
    
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    # Load and process data
    sales_data = load_sales_data()
    if not sales_data:
        st.warning("Waiting for initial data...")
        time.sleep(2)
        st.rerun()
    
    df = pd.DataFrame(sales_data)
    
    # Dashboard content (your existing visualization code)
    # ... [Include all your chart and metric code here] ...
    
    # Auto-refresh
    time.sleep(3)
    st.rerun()

# ========== APP INITIALIZATION ==========
if __name__ == "__main__":
    init_db()
    
    if not st.session_state.get('authenticated'):
        login_page()
    else:
        sales_dashboard()
