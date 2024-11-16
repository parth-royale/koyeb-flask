# from flask import Flask
# import pandas as pd
# import os

# app = Flask(__name__)

# # Define the path to the CSV file
# csv_file_path = os.path.join(os.path.dirname(__file__), "1.csv")

# @app.route('/')
# def hello_world():
#     # Check if CSV file exists; if not, display a message
#     if not os.path.exists(csv_file_path):
#         return "No CSV generated yet"
    
#     # Read the CSV file and display its content as HTML
#     df = pd.read_csv(csv_file_path)
#     return df.to_html()

# @app.route('/dfx')
# def generate_csv():
#     # Create the CSV file with sample data
#     data = {
#         'Open': [100, 110],
#         'High': [105, 115],
#         'Low': [95, 105],
#         'Close': [102, 112]
#     }
#     df = pd.DataFrame(data)
#     df.to_csv(csv_file_path, index=False)
#     return "CSV file '1.csv' has been created with sample data."

# if __name__ == "__main__":
#     app.run()


from flask import Flask, request, jsonify
import platform
from datetime import datetime
import user_agents

app = Flask(__name__)

def get_client_info():
    """Get detailed client information from the request"""
    # Get IP addresses
    client_ip = request.remote_addr
    forwarded_for = request.headers.get('X-Forwarded-For', 'Not available')
    real_ip = request.headers.get('X-Real-IP', 'Not available')
    
    # Get User Agent information
    user_agent_string = request.headers.get('User-Agent', 'Unknown')
    user_agent = user_agents.parse(user_agent_string)
    
    # Get additional headers
    headers = dict(request.headers)
    
    # Create client info dictionary
    client_info = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip_addresses': {
            'direct_client_ip': client_ip,
            'x_forwarded_for': forwarded_for,
            'x_real_ip': real_ip
        },
        'browser_info': {
            'browser_family': user_agent.browser.family,
            'browser_version': user_agent.browser.version_string,
            'os': user_agent.os.family,
            'os_version': user_agent.os.version_string,
            'device': user_agent.device.family,
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_pc': user_agent.is_pc,
            'is_bot': user_agent.is_bot
        },
        'request_info': {
            'method': request.method,
            'path': request.path,
            'protocol': request.scheme,
            'host': request.host,
        },
        'headers': headers
    }
    
    return client_info

@app.route('/')
def index():
    """Display client information in a formatted JSON response"""
    client_info = get_client_info()
    return jsonify(client_info)

@app.route('/raw')
def raw_info():
    """Display raw request information"""
    return {
        'environ': str(request.environ),
        'headers': dict(request.headers)
    }

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == "__main__":
    app.run()

