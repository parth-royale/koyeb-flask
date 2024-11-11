from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

# Define the path to the CSV file
csv_file_path = os.path.join(os.path.dirname(__file__), "1.csv")

@app.route('/')
def hello_world():
    # Check if CSV file exists; if not, display a message
    if not os.path.exists(csv_file_path):
        return "No CSV generated yet"
    
    # Read the CSV file and display its content as HTML
    df = pd.read_csv(csv_file_path)
    return df.to_html()

@app.route('/dfx')
def generate_csv():
    # Create the CSV file with sample data
    data = {
        'Open': [100, 110],
        'High': [105, 115],
        'Low': [95, 105],
        'Close': [102, 112]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_file_path, index=False)
    return "CSV file '1.csv' has been created with sample data."

if __name__ == "__main__":
    app.run()
