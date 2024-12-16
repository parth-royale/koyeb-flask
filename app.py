import csv
import os
import random
import time
from datetime import datetime
import psycopg2

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS

# Flask app setup
app = Flask(__name__)
CORS(app)

# Constants 
UPLOAD_INTERVAL = 4  # 20 seconds
CSV_FILE_PATH = 'one.csv'
CONNECTION_STRING = "postgresql://neondb_owner:p3wABei1NrGQ@ep-aged-dawn-a96td1sk.gwc.azure.neon.tech/neondb?sslmode=require"
# "postgresql://koyebdb_owner:tM6lmGPdJ1yQ@ep-shrill-mountain-a27t8n7h.eu-central-1.aws.neon.tech/koyebdb?sslmode=require"

# Utility functions
def create_csv_if_not_exists():
    """Create CSV file with header if it doesn't exist"""
    if not os.path.exists(CSV_FILE_PATH):
        print('CSV file not found, creating a new one...')
        header = ['column1', 'column2', 'timestamp']
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
        print('New CSV file created with header.')

def generate_random_data():
    """Generate a random data record"""
    return {
        'column1': random.randint(0, 1000),
        'column2': f"Value-{random.randint(0, 100)}",
        'timestamp': datetime.now().isoformat()
    }

def read_csv():
    """Read and return CSV records"""
    if os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    return []

def update_csv():
    """Update CSV with new random data"""
    try:
        create_csv_if_not_exists()

        # Read existing data
        records = read_csv()

        # Generate and add new row
        new_record = generate_random_data()
        records.append(new_record)

        # Write updated records to CSV
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['column1', 'column2', 'timestamp']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print('CSV file updated with new row:', new_record)
        return records
    except Exception as error:
        print('Error updating CSV:', error)
        raise error

def upload_csv_to_db(latest_record):
    """Upload latest record to PostgreSQL database"""
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        cursor = conn.cursor()

        print(f"Uploading the latest record: {latest_record}")

        # Insert the latest record into the database
        insert_query = """
            INSERT INTO your_table (column1, column2, timestamp)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (
            latest_record['column1'], 
            latest_record['column2'], 
            latest_record['timestamp']
        ))
        conn.commit()

        print('New data successfully uploaded to the database.')
    except Exception as error:
        if conn:
            conn.rollback()
        print('Error uploading data to the database:', error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def periodic_task():
    """Perform periodic CSV update and database upload"""
    while True:
        try:
            record = update_csv()
            latest_record = record[-1]
            upload_csv_to_db(latest_record)
            print(f"Latest record: {latest_record}")
            time.sleep(UPLOAD_INTERVAL)
        except Exception as e:
            print(f"Error in periodic task: {e}")
            time.sleep(UPLOAD_INTERVAL)

# Web routes
@app.route('/')
def index():
    """Render CSV data in an HTML table"""
    records = read_csv()
    template = """
    <html>
    <table border="1">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            {% for record in records %}
            <tr>
                <td>{{ record.column1 }}</td>
                <td>{{ record.column2 }}</td>
                <td>{{ record.timestamp }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    </html>
    """
    return render_template_string(template, records=records)

@app.route('/csv_data')
def csv_data():
    """Return CSV data as JSON"""
    records = read_csv()
    return jsonify(records)

# Gunicorn-friendly initialization
def start_background_thread():
    """Start background thread for periodic tasks"""
    import threading
    thread = threading.Thread(target=periodic_task, daemon=True)
    thread.start()
    return thread

# Initialize background thread when the app is imported
start_background_thread()

