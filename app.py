import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# ========== CLOUD CONFIG ==========
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "database", "admin.db")
DATA_PATH = os.path.join(BASE_DIR, "synthetic_logs.csv")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ========== DATABASE SETUP ==========
def init_db():
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

# ========== APP PAGES ==========
def login_page():
    st.title("🔒 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username = ?", (username,))
        admin = c.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin[2], password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

def dashboard():
    st.title("📊 Analytics Dashboard")
    st.write(f"Welcome, {st.session_state['username']}!")
    
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    try:
        df = pd.read_csv(DATA_PATH)
        
        # Metrics
        col1, col2 = st.columns(2)
        col1.metric("Total Requests", len(df))
        col2.metric("Unique Visitors", df['IP Address'].nunique())
        
        # Status Codes Chart
        st.subheader("🔄 Status Codes")
        status_counts = df['Status Code'].value_counts()
        fig1 = go.Figure(go.Bar(x=status_counts.index, y=status_counts.values))
        st.plotly_chart(fig1, use_container_width=True)
        
        # Endpoints Chart
        st.subheader("🔗 Top Endpoints")
        endpoints = df['Endpoint'].value_counts().head(5)
        fig2 = go.Figure(go.Pie(labels=endpoints.index, values=endpoints.values))
        st.plotly_chart(fig2, use_container_width=True)
        
    except FileNotFoundError:
        st.warning("⚠️ Waiting for log data...")
        # Generate sample data if missing
        sample_data = pd.DataFrame({
            'IP Address': ['192.168.1.1', '10.0.0.1'],
            'Status Code': [200, 404],
            'Endpoint': ['/home', '/api']
        })
        sample_data.to_csv(DATA_PATH, index=False)
        st.rerun()

# ========== APP INIT ==========
if __name__ == "__main__":
    init_db()
    
    if not st.session_state.get('authenticated'):
        login_page()
    else:
        dashboard()
