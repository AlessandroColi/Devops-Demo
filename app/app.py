from flask import Flask, render_template_string, request
import os
import socket
import time
from threading import Lock

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
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        .easter-egg {
            display: {% if easter_egg %}block{% else %}none{% endif %};
            color: #ffeb3b;
            font-size: 1.2em;
            margin-top: 20px;
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
        
        <p>This environment was created with Docker</p>
        <div class="hostname">Served from: {{ hostname }}</div>
    </div>
</body>
</html>
"""