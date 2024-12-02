import os
import random
import time
import csv
from datetime import datetime
from flask import Flask, render_template_string, jsonify
import psycopg2
from threading import Thread

# Flask app setup
app = Flask(__name__)



# File path for CSV
csv_file_path = 'one.csv'

# Time interval for uploads (in seconds)
upload_interval = 30  # 30 seconds

# Generate random data for new rows
def generate_random_data():
    return {
        'column1': random.randint(0, 1000),
        'column2': f"Value-{random.randint(0, 100)}",
        'timestamp': datetime.now().isoformat()
    }

# Check if CSV file exists, if not, create it with a header
def create_csv_if_not_exists():
    if not os.path.exists(csv_file_path):
        print('CSV file not found, creating a new one...')
        header = ['column1', 'column2', 'timestamp']
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
        print('New CSV file created with header.')

# Read CSV file and return the records
def read_csv():
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    return []

# Update CSV with new data
def update_csv():
    try:
        create_csv_if_not_exists()

        # Read existing data
        records = read_csv()
        print('Original CSV Data:', records)

        # Generate and add new row
        new_record = generate_random_data()
        records.append(new_record)

        # Write updated records to CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['column1', 'column2', 'timestamp']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print('CSV file updated with new row:', new_record)
        return records
    except Exception as error:
        print('Error updating CSV:', error)
        raise error

  
# Connect using the connection string
connection_string = "postgresql://koyebdb_owner:tM6lmGPdJ1yQ@ep-shrill-mountain-a27t8n7h.eu-central-1.aws.neon.tech/koyebdb?sslmode=require"

# Upload the latest CSV record to the database
def upload_csv_to_db():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    try:
        # Read and update the CSV first
        records = update_csv()

        # Get the latest record
        latest_record = records[-1]
        print(f"Uploading the latest record: {latest_record}")

        # Insert the latest record into the database
        insert_query = """
            INSERT INTO your_table (column1, column2, timestamp)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (latest_record['column1'], latest_record['column2'], latest_record['timestamp']))
        conn.commit()

        print('New data successfully uploaded to the database.')
    except Exception as error:
        conn.rollback()
        print('Error uploading data to the database:', error)
    finally:
        cursor.close()
        conn.close()

# Run the periodic upload in the background using a thread
def run_periodic_upload():
    while True:
        upload_csv_to_db()
        time.sleep(upload_interval)

# Start the periodic upload in a separate thread (directly in the main block)
def start_periodic_upload_thread():
    thread = Thread(target=run_periodic_upload)
    thread.daemon = True
    thread.start()

# Web route to display the status of the CSV and database upload
@app.route('/')
def index():
    return render_template_string(templat , upload_interval=upload_interval)

# Route to fetch the current CSV data and display in the table
@app.route('/csv_data')
def csv_data():
    # Read the CSV file and return the data as JSON
    records = read_csv()
    return jsonify(records)

# HTML template to display the current CSV and upload status
templat = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Upload Status</title>
    <script>
        // Function to update the table with the latest CSV data
        function fetchCSVData() {
            fetch('/csv_data')
                .then(response => response.json())
                .then(data => {
                    let tableBody = document.getElementById("csv-table-body");
                    tableBody.innerHTML = "";
                    data.forEach(record => {
                        let row = document.createElement("tr");
                        let col1 = document.createElement("td");
                        col1.textContent = record.column1;
                        let col2 = document.createElement("td");
                        col2.textContent = record.column2;
                        let timestamp = document.createElement("td");
                        timestamp.textContent = record.timestamp;
                        row.appendChild(col1);
                        row.appendChild(col2);
                        row.appendChild(timestamp);
                        tableBody.appendChild(row);
                    });
                });
        }

        // Fetch and update CSV data every 30 seconds
        setInterval(fetchCSVData, 30000);
    </script>
</head>
<body>
    <h1>CSV Upload Status</h1>
    <p>Data is being uploaded every {{ upload_interval }} seconds.</p>
    <p>Check your PostgreSQL database for the latest uploaded data.</p>

    <h2>Current CSV Data:</h2>
    <table border="1">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody id="csv-table-body">
            <!-- CSV data will be populated here -->
        </tbody>
    </table>
</body>
</html>
"""

if __name__ == "__main__":
    # Start the periodic upload in the background thread before running the Flask app
    start_periodic_upload_thread()

    # Run the Flask app
    app.run(debug=True)
