import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import time

# Config
DATA_PATH = "sales_dashboard_data.json"

def load_test_data():
    """Generate sample data if none exists"""
    if not os.path.exists(DATA_PATH):
        sample = [
            {
                "region_of_sales": "North",
                "final_price_after_discount": 100,
                "product_category": "Electronics"
            }
        ]
        with open(DATA_PATH, 'w') as f:
            json.dump(sample, f)

def sales_dashboard():
    load_test_data()
    
    with open(DATA_PATH) as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    st.write("Raw data:", data)
    st.write("DataFrame:", df)
    
    if not df.empty:
        st.title("Test Dashboard")
        
        # KPI
        st.metric("Total Sales", f"${df['final_price_after_discount'].sum()}")
        
        # Chart
        fig = px.bar(df, x='region_of_sales', y='final_price_after_discount')
        st.plotly_chart(fig)
    
    time.sleep(3)
    st.rerun()

# Remove authentication temporarily for testing
sales_dashboard()
