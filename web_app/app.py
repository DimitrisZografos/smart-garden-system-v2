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
import yaml
import random
import logging
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('smart_garden')

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

# Path to config
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.yaml')

# Load configuration
def load_config():
    """Load configuration from YAML file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    # Default configuration
    return {
        'watering': {
            'moisture_threshold': 30,
            'duration': 10
        },
        'weather': {
            'api_key': '',
            'location': 'London'
        },
        'camera': {
            'interval': 6,
            'rotation': 0
        }
    }

# Save configuration
def save_config(config):
    """Save configuration to YAML file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

# Sensor simulation class
class SensorManager:
    """Simulates sensor readings for the Smart Garden System"""
    
    def __init__(self):
        """Initialize the sensor manager in simulation mode"""
        logger.info("Initializing SensorManager in simulation mode")
        
        # Initialize simulation values
        self.sim_moisture = random.uniform(30, 70)
        self.sim_temp = random.uniform(18, 25)
        self.sim_humidity = random.uniform(40, 60)
        self.sim_pressure = random.uniform(1000, 1020)
    
    def read_soil_moisture(self):
        """Simulate soil moisture reading"""
        # Simulate slow changes in soil moisture
        change = random.uniform(-2, -0.5)  # Soil tends to dry out
        self.sim_moisture += change
        # Keep within realistic bounds
        self.sim_moisture = max(10, min(95, self.sim_moisture))
        logger.info(f"Simulated soil moisture: {self.sim_moisture:.1f}%")
        return round(self.sim_moisture, 1)
    
    def read_environmental_data(self):
        """Simulate temperature, humidity and pressure readings"""
        # Simulate small changes in environmental conditions
        temp_change = random.uniform(-0.5, 0.5)
        humidity_change = random.uniform(-1, 1)
        pressure_change = random.uniform(-1, 1)
        
        self.sim_temp += temp_change
        self.sim_humidity += humidity_change
        self.sim_pressure += pressure_change
        
        # Keep within realistic bounds
        self.sim_temp = max(10, min(35, self.sim_temp))
        self.sim_humidity = max(30, min(90, self.sim_humidity))
        self.sim_pressure = max(980, min(1040, self.sim_pressure))
        
        logger.info(f"Simulated environmental data: {self.sim_temp:.1f}°C, {self.sim_humidity:.1f}%, {self.sim_pressure:.1f}hPa")
        return (round(self.sim_temp, 1), round(self.sim_humidity, 1), round(self.sim_pressure, 1))
    
    def capture_image(self):
        """Simulate capturing an image"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(DATA_DIR, f"plant_{timestamp}.jpg")
        
        try:
            # Create a simple image with text
            img = Image.new('RGB', (1024, 768), color=(34, 139, 34))  # Green background
            draw = ImageDraw.Draw(img)
            
            # Try to use a font if available
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 32)
            except:
                font = ImageFont.load_default()
            
            # Add timestamp and simulated data
            draw.text((50, 50), f"Smart Garden System", fill=(255, 255, 255), font=font)
            draw.text((50, 100), f"Simulated Plant Image", fill=(255, 255, 255), font=font)
            draw.text((50, 150), f"Timestamp: {timestamp}", fill=(255, 255, 255), font=font)
            draw.text((50, 200), f"Soil Moisture: {self.sim_moisture:.1f}%", fill=(255, 255, 255), font=font)
            draw.text((50, 250), f"Temperature: {self.sim_temp:.1f}°C", fill=(255, 255, 255), font=font)
            draw.text((50, 300), f"Humidity: {self.sim_humidity:.1f}%", fill=(255, 255, 255), font=font)
            
            # Draw a simple plant
            # Stem
            draw.rectangle([(500, 400), (524, 700)], fill=(139, 69, 19))
            # Leaves
            draw.ellipse([(450, 350), (600, 450)], fill=(0, 100, 0))
            draw.ellipse([(400, 450), (550, 550)], fill=(0, 100, 0))
            draw.ellipse([(550, 450), (700, 550)], fill=(0, 100, 0))
            draw.ellipse([(475, 250), (575, 350)], fill=(0, 100, 0))
            
            # Save the image
            img.save(image_path)
            logger.info(f"Simulated image saved to {image_path}")
            return image_path
        except Exception as e:
            logger.error(f"Error creating simulated image: {e}")
            return None

# Watering system simulation class
class WateringSystem:
    """Simulates watering system for the Smart Garden System"""
    
    def __init__(self):
        """Initialize the watering system in simulation mode"""
        logger.info("Initializing WateringSystem in simulation mode")
        self.is_watering = False
    
    def water_plants(self, duration=10):
        """Simulate watering plants"""
        if self.is_watering:
            logger.warning("Watering system is already active")
            return False
        
        self.is_watering = True
        
        try:
            logger.info(f"[SIMULATED] Watering started for {duration} seconds")
            
            # In a real system, we would activate a relay here
            # For simulation, we just wait
            time.sleep(2)  # Reduced sleep time for better responsiveness
            
            logger.info("[SIMULATED] Watering completed")
            return True
        except Exception as e:
            logger.error(f"Error during watering: {e}")
            return False
        finally:
            self.is_watering = False

# Weather forecast simulation class
class WeatherForecast:
    """Simulates weather forecast for the Smart Garden System"""
    
    def __init__(self, api_key='', location='London'):
        """Initialize the weather forecast in simulation mode"""
        logger.info(f"Initializing WeatherForecast for {location}")
        self.api_key = api_key
        self.location = location
        self.last_update = 0
        self.forecast = "Simulated forecast: Partly cloudy with temperatures between 18°C and 25°C."
    
    def get_forecast(self):
        """Get weather forecast (simulated)"""
        # Update forecast every hour
        current_time = time.time()
        if current_time - self.last_update > 3600:
            self._update_forecast()
            self.last_update = current_time
        
        return self.forecast
    
    def _update_forecast(self):
        """Update the weather forecast (simulated)"""
        weather_types = ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain', 'Heavy rain']
        weather_type = random.choice(weather_types)
        
        min_temp = random.uniform(15, 20)
        max_temp = min_temp + random.uniform(5, 10)
        
        self.forecast = f"Simulated forecast: {weather_type} with temperatures between {min_temp:.1f}°C and {max_temp:.1f}°C."
        
        # Add rain probability if applicable
        if 'rain' in weather_type.lower():
            self.forecast += " High chance of precipitation."
        
        logger.info(f"Updated weather forecast: {self.forecast}")

# Initialize system components
config = load_config()
sensor_manager = SensorManager()
watering_system = WateringSystem()
weather_forecast = WeatherForecast(
    api_key=config.get('weather', {}).get('api_key', ''),
    location=config.get('weather', {}).get('location', 'London')
)

# Background thread to update data
def update_data_thread():
    """Background thread to update sensor data periodically"""
    while True:
        try:
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
            
            # Get weather forecast
            forecast = weather_forecast.get_forecast()
            if forecast:
                latest_data['weather_forecast'] = forecast
            
            # Save data to file
            save_data_to_file()
            
            # Take a picture every 6 hours (or as configured)
            current_hour = datetime.datetime.now().hour
            camera_interval = config.get('camera', {}).get('interval', 6)
            if current_hour % camera_interval == 0 and datetime.datetime.now().minute == 0:
                sensor_manager.capture_image()
            
            # Check if we need to water plants
            moisture_threshold = config.get('watering', {}).get('moisture_threshold', 30)
            if soil_moisture < moisture_threshold:
                watering_duration = config.get('watering', {}).get('duration', 10)
                if watering_system.water_plants(duration=watering_duration):
                    latest_data['last_watered'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    latest_data['watering_status'] = f"Auto watering for {watering_duration}s"
        
        except Exception as e:
            latest_data['system_status'] = f"Error: {str(e)}"
            logger.error(f"Error in update thread: {e}")
        
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
    return render_template('dashboard.html', data=latest_data, config=config)

@app.route('/api/data')
def api_data():
    """API endpoint to get the latest data"""
    return jsonify(latest_data)

@app.route('/api/history')
def api_history():
    """API endpoint to get historical data"""
    history_file = os.path.join(DATA_DIR, 'data_history.json')
    history_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    return jsonify(history_data)

@app.route('/api/water', methods=['POST'])
def api_water():
    """API endpoint to trigger manual watering"""
    duration = request.form.get('duration', 10)
    try:
        duration = int(duration)
    except:
        duration = 10
    
    if watering_system.water_plants(duration=duration):
        latest_data['last_watered'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_data['watering_status'] = f"Manual watering for {duration}s"
        return jsonify({'status': 'success', 'message': f'Watering for {duration} seconds'})
    else:
        return jsonify({'status': 'error', 'message': 'Watering system is busy'})

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

@app.route('/api/settings', methods=['POST'])
def api_settings():
    """API endpoint to save settings"""
    try:
        # Get current config
        current_config = load_config()
        
        # Update with form data
        current_config['watering']['moisture_threshold'] = int(request.form.get('moisture_threshold', 30))
        current_config['watering']['duration'] = int(request.form.get('watering_duration', 10))
        current_config['weather']['api_key'] = request.form.get('weather_api_key', '')
        current_config['weather']['location'] = request.form.get('weather_location', 'London')
        current_config['camera']['interval'] = int(request.form.get('camera_interval', 6))
        current_config['camera']['rotation'] = int(request.form.get('camera_rotation', 0))
        
        # Save updated config
        if save_config(current_config):
            # Update global config
            global config
            config = current_config
            
            # Update weather forecast with new settings
            global weather_forecast
            weather_forecast = WeatherForecast(
                api_key=config['weather']['api_key'],
                location=config['weather']['location']
            )
            
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save configuration'})
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def start_background_thread():
    """Start the background thread for data updates"""
    thread = threading.Thread(target=update_data_thread, daemon=True)
    thread.start()

if __name__ == '__main__':
    # Start background thread
    start_background_thread()
    
    # Run the Flask app
    # Use host='0.0.0.0' to make it accessible from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=False)