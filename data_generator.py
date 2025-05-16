import sqlite3
import json
import random
import time
import os
from datetime import datetime

# Configuration for sales data - Updated for AI solutions company
PRODUCT_CATEGORIES = [
    "Business Intelligence", 
    "Data Analytics", 
    "AI Solutions", 
    "ICT Infrastructure",
    "Cloud Services",
    "Predictive Modeling"
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Cash", "Bank Transfer"]
CUSTOMER_TYPES = ["New", "Returning", "Enterprise", "Government"]
INDUSTRIES = ["Finance", "Healthcare", "Retail", "Manufacturing", "Telecom"]
REGIONS = ["North", "South", "East", "West", "Central"]
CITIES = ["Gaborone", "Francistown", "Maun", "Serowe", "Molepolole", "Kanye"]
COUNTRIES = ["Botswana", "South Africa", "Namibia", "Zimbabwe"]
SALES_REPS = [
    "John Smith", 
    "Sarah Johnson", 
    "Michael Brown", 
    "Emily Davis", 
    "David Wilson"
]

def generate_product_name(category):
    """Generate realistic AI/tech product names based on category"""
    prefixes = {
        "Business Intelligence": ["Enterprise", "Advanced", "Executive", "Strategic"],
        "Data Analytics": ["Insight", "Analytic", "Data", "Intelligence"],
        "AI Solutions": ["AI", "Smart", "Cognitive", "Automated"],
        "ICT Infrastructure": ["Secure", "Cloud", "Network", "Infra"],
        "Cloud Services": ["Cloud", "Hybrid", "Enterprise", "Secure"],
        "Predictive Modeling": ["Predict", "Forecast", "Trend", "Future"]
    }
    base_names = {
        "Business Intelligence": ["Dashboard", "Suite", "Platform", "Analytics"],
        "Data Analytics": ["Engine", "Workbench", "Studio", "Hub"],
        "AI Solutions": ["Assistant", "Engine", "Solution", "Service"],
        "ICT Infrastructure": ["Framework", "Architecture", "System", "Solution"],
        "Cloud Services": ["Hosting", "Computing", "Storage", "Services"],
        "Predictive Modeling": ["Modeler", "Analyzer", "Forecaster", "Planner"]
    }
    prefix = random.choice(prefixes.get(category, ["Advanced", "Enterprise"]))
    base = random.choice(base_names.get(category, ["Solution", "Platform"]))
    return f"{prefix} {base} v{random.randint(1, 5)}.{random.randint(0, 9)}"

def create_sales_database():
    """Create SQLite database with updated sales table structure including sales rep"""
    conn = sqlite3.connect("sales_data.db")
    cursor = conn.cursor()
    
    # First drop the existing table if it has the old schema
    cursor.execute("DROP TABLE IF EXISTS sales")
    
    # Create new table with updated schema
    cursor.execute("""
    CREATE TABLE sales (
        sales_id TEXT PRIMARY KEY,
        product_id TEXT,
        product_name TEXT,
        product_category TEXT,
        total_sales_revenue REAL,
        number_of_transactions INTEGER,
        quantity_sold INTEGER,
        unit_price REAL,
        discount_applied_pct REAL,
        final_price_after_discount REAL,
        payment_method TEXT,
        country TEXT,
        region_of_sales TEXT,
        city TEXT,
        customer_type TEXT,
        industry TEXT,
        sales_rep TEXT,  -- This is the new column
        timestamp TEXT,
        date TEXT,
        ip_address TEXT,
        method TEXT,
        page_accessed TEXT,
        response_code INTEGER,
        user_agent TEXT
    )
    """)
    conn.commit()
    conn.close()

def verify_table_structure():
    """Verify the table has the correct structure before inserting data"""
    conn = sqlite3.connect("sales_data.db")
    cursor = conn.cursor()
    
    try:
        # Get table info
        cursor.execute("PRAGMA table_info(sales)")
        columns = cursor.fetchall()
        
        # Check if sales_rep column exists
        has_sales_rep = any(col[1] == 'sales_rep' for col in columns)
        
        if not has_sales_rep:
            print("⚠️ Table structure outdated - recreating table")
            create_sales_database()
    finally:
        conn.close()

def generate_sales_record():
    """Generate a complete sales transaction record with guaranteed unique ID"""
    timestamp = datetime.now()
    unique_id = f"SALE-{int(timestamp.timestamp() * 1000)}-{random.randint(1000, 9999)}"
    
    product_category = random.choice(PRODUCT_CATEGORIES)
    unit_price = round(random.uniform(1000, 25000), 2)  # Higher prices for enterprise software
    quantity = random.randint(1, 5)  # Typically selling fewer high-value items
    discount = random.choice([0, 5, 10, 15, 20, 25])  # Larger possible discounts
    
    total_sales = unit_price * quantity
    final_price = total_sales * (1 - discount/100)
    
    return {
        "sales_id": unique_id,
        "product_id": f"AI-{random.randint(1000, 9999)}",
        "product_name": generate_product_name(product_category),
        "product_category": product_category,
        "total_sales_revenue": round(total_sales, 2),
        "number_of_transactions": 1,
        "quantity_sold": quantity,
        "unit_price": unit_price,
        "discount_applied_pct": discount,
        "final_price_after_discount": round(final_price, 2),
        "payment_method": random.choice(PAYMENT_METHODS),
        "country": random.choice(COUNTRIES),
        "region_of_sales": random.choice(REGIONS),
        "city": random.choice(CITIES),
        "customer_type": random.choice(CUSTOMER_TYPES),
        "industry": random.choice(INDUSTRIES),
        "sales_rep": random.choice(SALES_REPS),  # Added sales rep field
        "timestamp": timestamp.isoformat(),
        "date": timestamp.strftime("%Y-%m-%d"),
        "ip_address": f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
        "method": random.choice(["GET", "POST"]),
        "page_accessed": f"/solution/{random.randint(1000, 9999)}",
        "response_code": random.choice([200, 201, 400, 404, 500]),
        "user_agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
        ])
    }

def generate_batch_data(num_records=5):
    """Generate multiple sales records at once"""
    return [generate_sales_record() for _ in range(num_records)]

def update_json_file(new_records):
    """Update the JSON file with new records while maintaining last 100 records"""
    try:
        # Try to load existing data
        if os.path.exists("sales_dashboard_data.json"):
            with open("sales_dashboard_data.json", "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    
    # Combine and limit to last 100 records
    updated_data = (existing_data + new_records)[-100:]
    
    # Save to file
    with open("sales_dashboard_data.json", "w") as f:
        json.dump(updated_data, f, indent=2, default=str)
    
    return len(new_records)

def insert_sales_record(record):
    """Insert a sales record into the database with error handling"""
    try:
        # Verify table structure before inserting
        verify_table_structure()
        
        conn = sqlite3.connect("sales_data.db")
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO sales VALUES (
            :sales_id, :product_id, :product_name, :product_category,
            :total_sales_revenue, :number_of_transactions, :quantity_sold, :unit_price,
            :discount_applied_pct, :final_price_after_discount, :payment_method,
            :country, :region_of_sales, :city, :customer_type, :industry, :sales_rep,
            :timestamp, :date, :ip_address, :method, :page_accessed, :response_code, :user_agent
        )
        """, record)
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"⚠️ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main data generation loop"""
    # Remove old database if it exists
    if os.path.exists("sales_data.db"):
        os.remove("sales_data.db")
    
    create_sales_database()  # Create fresh database with new schema
    
    while True:
        try:
            # Generate batch of sales records
            batch_size = random.randint(3, 8)
            sales_data = generate_batch_data(batch_size)
            
            # Insert into database
            successful_inserts = 0
            for record in sales_data:
                if insert_sales_record(record):
                    successful_inserts += 1
            
            # Update JSON file
            json_count = update_json_file(sales_data)
            
            print(f"✅ Generated {batch_size} records | DB: {successful_inserts}/{batch_size} inserted | JSON: {json_count} updated at {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Data generator stopped by user")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()