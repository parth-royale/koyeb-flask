

import csv, time
import os, random
from datetime import datetime
import psycopg2

from threading import Thread
from flask_cors import CORS
from flask import Flask, render_template_string, jsonify

# Flask app setup
app = Flask(__name__)

# Enable CORS for the entire app

# Restrict CORS if Needed (Optional): If you want to restrict access to specific origins, you can specify the allowed origins:

# CORS(app, resources={r"/csv_data": {"origins": "http://your-allowed-origin.com"}})

CORS(app)


# Constants 
upload_interval = 20  # 30 seconds
csv_file_path = 'one.csv'



# util0
# Check if CSV file exists, if not, create it with a header
def create_csv_if_not_exists():
    if not os.path.exists(csv_file_path):
        print('CSV file not found, creating a new one...')
        header = ['column1', 'column2', 'timestamp']
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
        print('New CSV file created with header.')


# util1 
# Generate random data for new rows
def generate_random_data():
    return {
        'column1': random.randint(0, 1000),
        'column2': f"Value-{random.randint(0, 100)}",
        'timestamp': datetime.now().isoformat()
    }


#util2
# Read CSV file and return the records
def read_csv():
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    return []


# util3

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
def upload_csv_to_db(latest_record):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    try:
        # # Read and update the CSV first
        # records = update_csv()

        # # Get the latest record
        # latest_record = records[-1]
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

def run_periodic_upload():
    while True:    
        record = update_csv()
        latest_record = record[-1]
        upload_csv_to_db(latest_record)
        print(f"the latest record: {latest_record}###########################")
        time.sleep(upload_interval)


def start_periodic_upload_thread():
    thread = Thread(target=run_periodic_upload)
    thread.daemon = True
    thread.start()





# Web route to display the status of the CSV and database upload
@app.route('/')
def index():
    # Read the CSV data to pass to the template
    records = read_csv()
    # Define the template inline
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



# Route to fetch the current CSV data and display in the table
@app.route('/csv_data')
def csv_data():
    # Read the CSV file and return the data as JSON
    records = read_csv()
    return jsonify(records)




# main blcok 



if __name__ == "__main__":
    # Start the periodic upload in the background thread before running the Flask app
    start_periodic_upload_thread()

    # Run the Flask app
    app.run(debug=False)


