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

# Set page config
st.set_page_config(page_title="Real-Time Sales Dashboard", layout="wide")

# Initialize session state
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = []
    st.session_state.last_update = 0

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
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: var(--primary-color);
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
    }
    .stMetric {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
    }
    .download-btn {
        background: linear-gradient(135deg, #00f2ff, #ff00e6);
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        margin-top: 10px;
    }
    .download-btn:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def load_sales_data():
    """Load and validate sales data"""
    try:
        filepath = os.path.abspath("sales_dashboard_data.json")
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump([], f)
            return []
        
        current_mod_time = os.path.getmtime(filepath)
        if current_mod_time > st.session_state.last_update:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):  # Ensure proper format
                    return []
                st.session_state.last_update = current_mod_time
                return data
        return st.session_state.sales_data
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        return []

def get_historical_data():
    """Fetch all historical data from SQLite database"""
    try:
        conn = sqlite3.connect('sales_data.db')
        query = "SELECT * FROM sales ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def create_kpi_card(value, label):
    return st.metric(label=label, value=value)

def create_chart(chart_type, data, **kwargs):
    if chart_type == 'bar':
        fig = px.bar(data, **kwargs)
    elif chart_type == 'pie':
        fig = px.pie(data, **kwargs)
    elif chart_type == 'line':
        fig = px.line(data, **kwargs)
    
    fig.update_layout(
        plot_bgcolor='rgba(20, 20, 40, 0.7)',
        paper_bgcolor='rgba(20, 20, 40, 0.7)',
        font_color='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Main dashboard
st.title("📊 Real-Time Sales Dashboard")
st.markdown("---")

# Navigation filters
col1, col2 = st.columns(2)
with col1:
    region_filter = st.multiselect(
        "Select Regions",
        options=["North", "South", "East", "West", "Central"],
        default=[]
    )
with col2:
    category_filter = st.multiselect(
        "Select Categories",
        options=["Business Intelligence", 
    "Data Analytics", 
    "AI Solutions", 
    "ICT Infrastructure",
    "Cloud Services",
    "Predictive Modeling"],
        default=[]
    )

# Load and filter data
sales_data = load_sales_data()
if not sales_data:
    st.warning("Waiting for initial data...")
    time.sleep(2)
    st.rerun()

df = pd.DataFrame(sales_data)

if region_filter or category_filter:
    df = df[
        (df['region_of_sales'].isin(region_filter) if region_filter else True) & 
        (df['product_category'].isin(category_filter) if category_filter else True)
    ]

# ✅ Data Export Section (after df is defined)
st.markdown("### Data Export")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    csv_current = df.to_csv(index=False).encode('utf-8') if not df.empty else None
    st.download_button(
        label="⬇️ Download Current View",
        data=csv_current,
        file_name='current_sales_data.csv',
        mime='text/csv',
        disabled=csv_current is None,
        help="Download currently filtered data"
    )

with col_exp2:
    historical_df = get_historical_data()
    csv_historical = historical_df.to_csv(index=False).encode('utf-8') if not historical_df.empty else None
    st.download_button(
        label="⬇️ Download Full History",
        data=csv_historical,
        file_name='full_sales_history.csv',
        mime='text/csv',
        disabled=csv_historical is None,
        help="Download complete historical data from database"
    )

# KPI Cards - Removed Transactions and Top Region cards
st.subheader("Key Metrics")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    create_kpi_card(f"P{df['final_price_after_discount'].sum():,.2f}", "Total Revenue")
with kpi2:
    create_kpi_card(f"P{df['final_price_after_discount'].mean():,.2f}", "Avg Order")
with kpi3:
    create_kpi_card(df['product_name'].mode()[0], "Top Product")

# Charts with added headings
st.subheader("Sales Analytics")

# First row of charts
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Revenue by Region")
    region_sales = df.groupby('region_of_sales')['final_price_after_discount'].sum().reset_index()
    fig = px.bar(region_sales, x='region_of_sales', y='final_price_after_discount')
    
    # Add regional target line (20% above mean)
    regional_target = region_sales['final_price_after_discount'].mean() * 1.2
    fig.add_hline(y=regional_target, line_dash="dot", 
                 annotation_text=f"Target: P{regional_target:,.2f}", 
                 line_color="#ff00e6")
    
    fig.update_layout(
        plot_bgcolor='rgba(20, 20, 40, 0.7)',
        paper_bgcolor='rgba(20, 20, 40, 0.7)',
        font_color='white'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Product Category Distribution")
    category_sales = df['product_category'].value_counts().reset_index()
    category_sales.columns = ['product_category', 'count']
    st.plotly_chart(
        create_chart('pie', category_sales, names='product_category', values='count'),
        use_container_width=True
    )

# Second row of charts
col3, col4 = st.columns(2)
with col3:
    st.markdown("#### Revenue by Customer Type")
    customer_sales = df.groupby('customer_type')['final_price_after_discount'].sum().reset_index()
    
    # Create line graph with proper connections
    fig = px.line(customer_sales, 
                 x='customer_type', 
                 y='final_price_after_discount',
                 markers=True,
                 template='plotly_dark',
                 text='final_price_after_discount',
                 labels={'final_price_after_discount': 'Revenue (P)'})
    
    # Style enhancements
    fig.update_traces(
        line_shape='linear',  # Ensures direct point-to-point connection
        line_width=4,
        marker_size=12,
        texttemplate='P%{y:,.2f}',
        textposition='top center'
    )
    
    # Add target line (example: 20% above mean)
    target = customer_sales['final_price_after_discount'].mean() * 1.2
    fig.add_hline(y=target, line_dash="dot", 
                 line_color="#ff00e6",
                 annotation_text=f"Target: P{target:,.2f}",
                 annotation_position="bottom right")
    
    fig.update_layout(
        xaxis_title='Customer Type',
        yaxis_title='Total Revenue',
        showlegend=False,
        hovermode="x unified",
        plot_bgcolor='rgba(20, 20, 40, 0.7)',
        paper_bgcolor='rgba(20, 20, 40, 0.7)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.markdown("#### Payment Method Distribution")
    payment_counts = df['payment_method'].value_counts().reset_index()
    payment_counts.columns = ['payment_method', 'count']
    fig = px.pie(payment_counts, names='payment_method', values='count', 
                 hole=0.3, template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# Third row of charts
col5, col6 = st.columns(2)
with col5:
    st.markdown("#### Top 5 Products by Revenue")
    top_products = df.groupby('product_name')['final_price_after_discount'].sum().nlargest(5).reset_index()
    
    # Calculate single target (average of top 5 + 20%)
    avg_top5 = top_products['final_price_after_discount'].mean()
    target = avg_top5 * 1.2
    
    fig = px.bar(top_products, y='product_name', x='final_price_after_discount', 
                 orientation='h', template='plotly_dark',
                 labels={'final_price_after_discount': 'Revenue (P)'})
    
    # Add single target line
    fig.add_vline(x=target, line_dash="dot", line_color="#ff00e6",
                 annotation_text=f"Target: P{target:,.2f}", 
                 annotation_position="top right")
    
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='rgba(20, 20, 40, 0.7)',
        paper_bgcolor='rgba(20, 20, 40, 0.7)'
    )
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.markdown("#### Price vs Quantity Scatter Plot")
    # Create scatter plot of unit price vs quantity sold, colored by product category
    fig = px.scatter(df, x='unit_price', y='quantity_sold',
                     color='product_category',
                     size='final_price_after_discount',
                     hover_name='product_name',
                     template='plotly_dark',
                     labels={
                         'unit_price': 'Unit Price (P)',
                         'quantity_sold': 'Quantity Sold',
                         'product_category': 'Category'
                     })
    
    # Add target zones
    fig.add_vrect(x0=5000, x1=10000, fillcolor="#00f2ff", opacity=0.1,
                 annotation_text="Premium Range", annotation_position="top left")
    
    fig.add_hrect(y0=3, y1=6, fillcolor="#ff00e6", opacity=0.1,
                 annotation_text="Bulk Range", annotation_position="bottom right")
    
    st.plotly_chart(fig, use_container_width=True)

# Fourth row - Sales Rep Performance with Targets
st.markdown("#### Sales Performance by Representative")
sales_rep_performance = df.groupby('sales_rep').agg({
    'final_price_after_discount': 'sum',
    'number_of_transactions': 'count'
}).reset_index()

# Calculate target (mean + 15%)
rep_target = sales_rep_performance['final_price_after_discount'].mean() * 1.15

fig = px.bar(sales_rep_performance, x='sales_rep', y='final_price_after_discount',
             hover_data=['number_of_transactions'], template='plotly_dark',
             labels={'final_price_after_discount': 'Total Revenue'})

# Add target line and highlight top performers
fig.add_hline(y=rep_target, line_dash="dot", line_color="#00f2ff",
             annotation_text=f"Target: P{rep_target:,.2f}")

st.plotly_chart(fig, use_container_width=True)

# Auto-refresh
time.sleep(3)
st.rerun()