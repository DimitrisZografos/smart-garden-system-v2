#!/usr/bin/env python3
"""
Smart Garden System Web Interface
This module provides a web interface for the Smart Garden System.
It runs on the Raspberry Pi and can be accessed from any device on the network.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import sys
import json
import datetime
import threading
import time

# Add parent directory to path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main project
try:
    from sensors import SensorManager
    from actuators import WateringSystem
    from weather import WeatherForecast
except ImportError:
    print("Warning: Could not import main project modules. Running in standalone mode.")

# Initialize Flask app
app = Flask(__name__)

# Global variables to store the latest data
latest_data = {
    'soil_moisture': 0,
    'temperature': 0,
    'humidity': 0,
    'pressure': 0,
    'last_watered': 'Never',
    'watering_status': 'Idle',
    'weather_forecast': 'Unknown',
    'last_updated': 'Never',
    'system_status': 'Starting...'
}

# Path to store images and data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize sensor manager in simulation mode for the web app
sensor_manager = None
watering_system = None
weather_forecast = None

def initialize_systems():
    """Initialize all system components"""
    global sensor_manager, watering_system, weather_forecast
    
    # Initialize with simulation mode if not on Raspberry Pi
    try:
        sensor_manager = SensorManager(simulate=True)
        watering_system = WateringSystem(simulate=True)
        
        # Try to load config for weather
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
        if os.path.exists(config_path):
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if 'weather' in config and 'api_key' in config['weather']:
                    weather_forecast = WeatherForecast(config['weather']['api_key'], 
                                                      config['weather'].get('location', 'London'))
    except Exception as e:
        print(f"Error initializing systems: {e}")
        latest_data['system_status'] = f"Error: {str(e)}"

# Background thread to update data
def update_data_thread():
    """Background thread to update sensor data periodically"""
    while True:
        try:
            if sensor_manager:
                # Get sensor readings
                soil_moisture = sensor_manager.read_soil_moisture()
                temp, humidity, pressure = sensor_manager.read_environmental_data()
                
                # Update latest data
                latest_data['soil_moisture'] = soil_moisture
                latest_data['temperature'] = temp
                latest_data['humidity'] = humidity
                latest_data['pressure'] = pressure
                latest_data['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                latest_data['system_status'] = 'Running'
                
                # Get weather forecast if available
                if weather_forecast:
                    forecast = weather_forecast.get_forecast()
                    if forecast:
                        latest_data['weather_forecast'] = forecast
                
                # Save data to file
                save_data_to_file()
                
                # Take a picture if camera is available
                sensor_manager.capture_image()
            
        except Exception as e:
            latest_data['system_status'] = f"Error: {str(e)}"
            print(f"Error in update thread: {e}")
        
        # Sleep for 60 seconds before next update
        time.sleep(60)

def save_data_to_file():
    """Save the latest data to a JSON file"""
    data_file = os.path.join(DATA_DIR, 'latest_data.json')
    with open(data_file, 'w') as f:
        json.dump(latest_data, f)
    
    # Also append to history file
    history_file = os.path.join(DATA_DIR, 'data_history.json')
    history_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    # Add timestamp to current data
    current_data = latest_data.copy()
    current_data['timestamp'] = datetime.datetime.now().isoformat()
    
    # Limit history to 1000 entries
    history_data.append(current_data)
    if len(history_data) > 1000:
        history_data = history_data[-1000:]
    
    with open(history_file, 'w') as f:
        json.dump(history_data, f)

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', data=latest_data)

@app.route('/history')
def history():
    """Historical data page"""
    history_file = os.path.join(DATA_DIR, 'data_history.json')
    history_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    return render_template('history.html', history=history_data)

@app.route('/images')
def images():
    """Plant images gallery page"""
    images = []
    for file in os.listdir(DATA_DIR):
        if file.endswith('.jpg') or file.endswith('.png'):
            images.append({
                'filename': file,
                'url': url_for('static', filename=f'../../../data/{file}'),
                'date': datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(DATA_DIR, file))).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Sort by date, newest first
    images.sort(key=lambda x: x['date'], reverse=True)
    return render_template('images.html', images=images)

@app.route('/settings')
def settings():
    """Settings page"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
    config = {}
    if os.path.exists(config_path):
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    
    return render_template('settings.html', config=config)

@app.route('/api/data')
def api_data():
    """API endpoint to get the latest data"""
    return jsonify(latest_data)

@app.route('/api/water', methods=['POST'])
def api_water():
    """API endpoint to trigger manual watering"""
    duration = request.form.get('duration', 10)
    try:
        duration = int(duration)
    except:
        duration = 10
    
    if watering_system:
        watering_system.water_plants(duration=duration)
        latest_data['last_watered'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_data['watering_status'] = f"Manual watering for {duration}s"
        return jsonify({'status': 'success', 'message': f'Watering for {duration} seconds'})
    else:
        return jsonify({'status': 'error', 'message': 'Watering system not initialized'})

@app.route('/api/images')
def api_images():
    """API endpoint to get list of available images"""
    images = []
    for file in os.listdir(DATA_DIR):
        if file.endswith('.jpg') or file.endswith('.png'):
            images.append({
                'filename': file,
                'url': url_for('static', filename=f'../../../data/{file}'),
                'date': datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(DATA_DIR, file))).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Sort by date, newest first
    images.sort(key=lambda x: x['date'], reverse=True)
    return jsonify(images)

def start_background_thread():
    """Start the background thread for data updates"""
    thread = threading.Thread(target=update_data_thread, daemon=True)
    thread.start()

if __name__ == '__main__':
    # Initialize systems
    initialize_systems()
    
    # Start background thread
    start_background_thread()
    
    # Run the Flask app
    # Use host='0.0.0.0' to make it accessible from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=False)