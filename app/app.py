from flask import Flask, render_template_string, request, jsonify
import os
import socket
import time
from threading import Lock
from datetime import datetime
import random

app = Flask(__name__)

app_config = {
    'message': 'Welcome to Version 3.0!',
    'version': '3.0',
    'last_updated': time.time(),
    'easter_egg': False,
    'click_count': 0,
    'last_click_time': 0
}
config_lock = Lock()

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
            cursor: default;
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
            position: relative;
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
        .secret-area {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 50px;
            height: 50px;
            cursor: pointer;
            z-index: 100;
            transition: transform 0.3s ease;
        }
        .secret-area:hover {
            transform: scale(1.1);
        }
        .rocket-image {
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
        }
        .easter-egg {
            display: {% if easter_egg %}block{% else %}none{% endif %};
            color: #ffeb3b;
            font-size: 1.2em;
            margin-top: 20px;
            animation: rainbow 2s infinite;
        }
        @keyframes rainbow {
            0% { color: #ff0000; }
            16% { color: #ff8000; }
            33% { color: #ffff00; }
            50% { color: #00ff00; }
            66% { color: #0080ff; }
            83% { color: #8000ff; }
            100% { color: #ff0000; }
        }
        .hidden-text {
            color: rgba(255,255,255,0.3);
            font-size: 0.7em;
            margin: 5px 0;
        }
        .status {
            color: #4CAF50;
            font-weight: bold;
        }
        .update-form {
            margin-top: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        .update-form input {
            padding: 8px;
            border: none;
            border-radius: 4px;
            margin-right: 10px;
            width: 200px;
        }
        .update-form button {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .update-form button:hover {
            background: #764ba2;
        }
        .devops-message {
            font-size: 1.1em;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="secret-area" onclick="incrementClick()">
            <svg class="rocket-image" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13.5 10.5L21 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M13 7L17 11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M9.5 4.5C9.5 5.88071 10.6193 7 12 7C13.3807 7 14.5 5.88071 14.5 4.5C14.5 3.11929 13.3807 2 12 2C10.6193 2 9.5 3.11929 9.5 4.5Z" stroke="currentColor" stroke-width="2"/>
                <path d="M16 12C16 11.4477 16.4477 11 17 11C17.5523 11 18 11.4477 18 12V16C18 18.2091 16.2091 20 14 20H10C7.79086 20 6 18.2091 6 16V12C6 11.4477 6.44772 11 7 11C7.55228 11 8 11.4477 8 12V16C8 17.1046 8.89543 18 10 18H14C15.1046 18 16 17.1046 16 16V12Z" fill="currentColor"/>
                <path d="M4.5 13.5L3 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M19.5 13.5L21 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 11V14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        
        <h1>On-Demand Staging Environment</h1>
        <div class="message">{{ message }}</div>
        <div class="counter">Page Views: {{ count }}</div>
        <div>Version: {{ version }}</div>
        <div>Last Updated: {{ last_updated }}</div>
        
        <div class="easter-egg" id="easterEgg">
            <div class="devops-message" id="devopsMessage">WOW an easterEgg</div>
        </div>
        
        
        
    </div>

    <script>
        let clickCount = 0;
        const CLICKS_NEEDED = 5;
        const TIME_LIMIT = 3000;
        
        const devopsMessages = [
            "Infrastructure as Code? More like Infrastructure as Joke! 😄",
            "No servers were harmed in the making of this easter egg! 🖥️",
            "Your YAML file finally parsed correctly! 🎯",
            "DevOps magic is real! (Unlike most test coverage) ✨",
            "Your Terraform plan: +1 easter egg, -1 boredom 🏗️",
            "Git push --force approved for this feature! 💪",
            "Monitoring shows you're having too much fun! 📈",
            "Your PR was approved by the easter bunny! 🐇"
        ];
        
        function showEasterEgg() {
            const randomMessage = devopsMessages[Math.floor(Math.random() * devopsMessages.length)];
            document.getElementById('devopsMessage').textContent = randomMessage;
            document.getElementById('easterEgg').style.display = 'block';
            clickCount = 0;
        }
        
        function incrementClick() {
            clickCount++;
            const now = Date.now();
            
            fetch('/secret_click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({click_count: clickCount, timestamp: now})
            });
            
            // Check if easter egg should be triggered
            if (clickCount >= CLICKS_NEEDED) {
                fetch('/trigger_easter_egg')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showEasterEgg();
                            document.getElementById('hiddenText').style.display = 'none';
                        } else {
                            clickCount = 0;
                            document.getElementById('hiddenText').innerHTML = 'Too slow! Try clicking faster!';
                            setTimeout(() => {
                                document.getElementById('hiddenText').style.display = 'none';
                            }, 2000);
                        }
                    });
            }
            
            setTimeout(() => {
                if (clickCount < CLICKS_NEEDED) {
                    clickCount = 0;
                    document.getElementById('hiddenText').style.display = 'none';
                }
            }, TIME_LIMIT);
        }
    </script>
</body>
</html>
"""

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
        click_count = app_config['click_count']
    
    app.view_counter += 1
    
    hostname = socket.gethostname()
    
    return render_template_string(HTML_TEMPLATE, 
                                 message=message, 
                                 version=version, 
                                 last_updated=datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S'),
                                 easter_egg=easter_egg,
                                 count=app.view_counter,
                                 hostname=hostname,
                                 total_clicks=click_count,
                                 clicks_to_go=max(0, 5 - click_count))

@app.route('/secret_click', methods=['POST'])
def secret_click():
    """Track secret clicks"""
    data = request.get_json()
    with config_lock:
        app_config['click_count'] = data.get('click_count', 0)
        app_config['last_click_time'] = data.get('timestamp', 0)
    
    return jsonify({'success': True, 'click_count': app_config['click_count']})

@app.route('/trigger_easter_egg')
def trigger_easter_egg():
    """Trigger easter egg if conditions are met"""
    with config_lock:
        current_time = time.time() * 1000
        time_diff = current_time - app_config['last_click_time']
        
        if app_config['click_count'] >= 5 and time_diff <= 3000:
            app_config['easter_egg'] = True
            app_config['last_updated'] = time.time()
            return jsonify({'success': True, 'message': 'Easter egg activated!'})
        else:
            app_config['click_count'] = 0
            return jsonify({'success': False, 'message': 'Too slow! Try again faster!'})
        
#         <div class="update-form">
#             <h3>Live Update Demo</h3>
#             <form method="POST" action="/update">
#                 <input type="text" name="new_message" placeholder="Enter new message" value="{{ message }}">
#                 <button type="submit">Update Message</button>
#             </form>
#         </div>

# @app.route('/update', methods=['POST'])
# def update_message():
#     """Update the message via API"""
#     new_message = request.form.get('new_message', '')
#     if new_message:
#         with config_lock:
#             app_config['message'] = new_message
#             app_config['last_updated'] = time.time()
    
#     return index()

@app.route('/toggle_easter_egg', methods=['POST'])
def toggle_easter_egg():
    """Toggle easter egg manually"""
    with config_lock:
        app_config['easter_egg'] = not app_config['easter_egg']
        app_config['last_updated'] = time.time()
    
    return index()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)