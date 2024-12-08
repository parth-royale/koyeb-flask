import os
import pandas as pd
import random
from flask import Flask
import time

app = Flask(__name__)

# Define the path to the CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "1.csv")
GENERATION_INTERVAL = 2  # 2 seconds

# Global variable to track last generation time
last_generation_time = 0

def generate_data():
    """Generate sample financial data"""
    return {
        'Timestamp': time.time(),
        'Open': random.uniform(100, 120),
        'High': random.uniform(105, 125),
        'Low': random.uniform(90, 105),
        'Close': random.uniform(100, 115)
    }

def ensure_fresh_data():
    """Ensure CSV is appended with new data"""
    global last_generation_time
    current_time = time.time()
    
    # Check if it's time to generate new data
    if current_time - last_generation_time >= GENERATION_INTERVAL:
        # Create a new DataFrame with a single row of data
        new_data = pd.DataFrame([generate_data()])
        
        # Check if CSV exists
        if os.path.exists(CSV_FILE_PATH):
            # Append to existing CSV
            new_data.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)
        else:
            # Create new CSV with headers
            new_data.to_csv(CSV_FILE_PATH, index=False)
        
        # Update last generation time
        last_generation_time = current_time

@app.route('/')
def hello_world():
    """Route to display CSV contents"""
    # Ensure fresh data is generated
    ensure_fresh_data()
    
    # Read and display the CSV
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        return df.to_html()
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

@app.route('/rows')
def get_row_count():
    """Route to get number of rows in CSV"""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        return f"Total rows: {len(df)}"
    except Exception as e:
        return f"Error counting rows: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
