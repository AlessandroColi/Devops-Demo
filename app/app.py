from flask import Flask, render_template_string, request, jsonify
import os
import socket
import time
from threading import Lock
from datetime import datetime

app = Flask(__name__)

# Configuration that can be updated live
app_config = {
    'message': os.environ.get('APP_MESSAGE', 'Welcome to Version 1.0!'),
    'version': os.environ.get('APP_VERSION', '1.0'),
    'last_updated': time.time(),
    'easter_egg': False
}
config_lock = Lock()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>On-Demand Staging Demo</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            background: rgba(255, 255, 255, 0.1); 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            text-align: center;
            max-width: 600px;
            margin: 0 auto;
        }
        h1 { 
            color: white; 
            margin-bottom: 20px;
        }
        .message { 
            font-size: 1.5em; 
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
        }
        .counter { 
            font-size: 2em; 
            margin: 20px 0;
            color: #ffeb3b;
        }
        .update-form {
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }
        input[type="text"] {
            padding: 8px;
            border: none;
            border-radius: 4px;
            margin-right: 10px;
            width: 300px;
        }
        button {
            background: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        .easter-egg {
            display: {% if easter_egg %}block{% else %}none{% endif %};
            color: #ffeb3b;
            font-size: 1.2em;
            margin-top: 20px;
        }
        .status {
            color: #4CAF50;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>On-Demand Staging Environment</h1>
        <div class="message">{{ message }}</div>
        <div class="counter">Page Views: {{ count }}</div>
        <div>Version: {{ version }}</div>
        <div>Last Updated: {{ last_updated }}</div>
        
        <div class="update-form">
            <h3>Live Update Demo</h3>
            <form method="POST" action="/update">
                <input type="text" name="new_message" placeholder="Enter new message" value="{{ message }}">
                <button type="submit">Update Message</button>
            </form>
            <form method="POST" action="/toggle_easter_egg" style="margin-top: 10px;">
                <button type="submit">Toggle Easter Egg</button>
            </form>
        </div>
        
        <div class="easter-egg">
            🎉 You found the easter egg! DevOps rocks! 🚀
        </div>
    </div>
</body>
</html>
"""

# Initialize counter
if not hasattr(app, 'view_counter'):
    app.view_counter = 0

@app.route('/')
def index():
    """Main page route"""
    with config_lock:
        message = app_config['message']
        version = app_config['version']
        last_updated = app_config['last_updated']
        easter_egg = app_config['easter_egg']
    
    # Increment view counter
    app.view_counter += 1
    
    hostname = socket.gethostname()
    
    return render_template_string(HTML_TEMPLATE, 
                                 message=message, 
                                 version=version, 
                                 last_updated=datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S'),
                                 easter_egg=easter_egg,
                                 count=app.view_counter,
                                 hostname=hostname)

@app.route('/update', methods=['POST'])
def update_message():
    """Update the message via API"""
    new_message = request.form.get('new_message', '')
    if new_message:
        with config_lock:
            app_config['message'] = new_message
            app_config['last_updated'] = time.time()
    
    return index()

@app.route('/toggle_easter_egg', methods=['POST'])
def toggle_easter_egg():
    """Toggle easter egg"""
    with config_lock:
        app_config['easter_egg'] = not app_config['easter_egg']
        app_config['last_updated'] = time.time()
    
    return index()

@app.route('/api/health')
def health_check():
    """Health check endpoint for deployment verification"""
    return jsonify({
        'status': 'healthy',
        'message': app_config['message'],
        'version': app_config['version'],
        'timestamp': app_config['last_updated']
    })

@app.route('/api/update', methods=['POST'])
def api_update():
    """API endpoint for updating message (used by update.sh)"""
    data = request.get_json()
    if data and 'message' in data:
        with config_lock:
            app_config['message'] = data['message']
            app_config['last_updated'] = time.time()
        
        return jsonify({
            'status': 'success',
            'message': 'Message updated successfully',
            'new_message': app_config['message']
        })
    
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)