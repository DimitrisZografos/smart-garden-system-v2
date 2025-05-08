"""
Web interface for the Smart Garden System.
Provides a dashboard for monitoring and controlling the system.
"""

import os
import logging
import time
from typing import Dict, Any, Optional

from flask import Flask, render_template, jsonify, request, send_from_directory

logger = logging.getLogger(__name__)

def create_app(system):
    """
    Create the Flask application.
    
    Args:
        system: The SmartGardenSystem instance
        
    Returns:
        The Flask application
    """
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Ensure template and static directories exist
    os.makedirs('../templates', exist_ok=True)
    os.makedirs('../static', exist_ok=True)
    
    # Create a simple index.html if it doesn't exist
    if not os.path.exists('../templates/index.html'):
        with open('../templates/index.html', 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Garden System</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .card h2 {
            margin-top: 0;
            color: #3498db;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .sensor-value {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        .controls {
            margin-top: 20px;
            text-align: center;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover {
            background-color: #2980b9;
        }
        .status {
            margin-top: 10px;
            text-align: center;
            font-style: italic;
        }
        .chart {
            width: 100%;
            height: 200px;
            margin-top: 20px;
        }
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Smart Garden System</h1>
        
        <div class="dashboard">
            <div class="card">
                <h2>Soil Moisture</h2>
                <div class="sensor-value" id="soil-moisture">--</div>
                <div class="chart" id="soil-moisture-chart"></div>
            </div>
            
            <div class="card">
                <h2>Temperature</h2>
                <div class="sensor-value" id="temperature">--</div>
                <div class="chart" id="temperature-chart"></div>
            </div>
            
            <div class="card">
                <h2>Humidity</h2>
                <div class="sensor-value" id="humidity">--</div>
                <div class="chart" id="humidity-chart"></div>
            </div>
            
            <div class="card">
                <h2>Pressure</h2>
                <div class="sensor-value" id="pressure">--</div>
                <div class="chart" id="pressure-chart"></div>
            </div>
            
            <div class="card">
                <h2>Watering Control</h2>
                <div class="controls">
                    <button id="water-now">Water Now</button>
                </div>
                <div class="status" id="watering-status">Last watered: --</div>
            </div>
            
            <div class="card">
                <h2>Weather Forecast</h2>
                <div id="weather-forecast">Loading forecast...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Fetch sensor data
        function updateSensorData() {
            fetch('/api/sensors')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('soil-moisture').textContent = data.soil_moisture + '%';
                    document.getElementById('temperature').textContent = data.temperature + '°C';
                    document.getElementById('humidity').textContent = data.humidity + '%';
                    document.getElementById('pressure').textContent = data.pressure + ' hPa';
                })
                .catch(error => console.error('Error fetching sensor data:', error));
        }
        
        // Fetch watering status
        function updateWateringStatus() {
            fetch('/api/watering/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('watering-status').textContent = 'Last watered: ' + data.last_watered;
                })
                .catch(error => console.error('Error fetching watering status:', error));
        }
        
        // Fetch weather forecast
        function updateWeatherForecast() {
            fetch('/api/weather')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('weather-forecast').textContent = data.summary;
                })
                .catch(error => console.error('Error fetching weather forecast:', error));
        }
        
        // Water now button
        document.getElementById('water-now').addEventListener('click', function() {
            fetch('/api/watering/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateWateringStatus();
                })
                .catch(error => console.error('Error starting watering:', error));
        });
        
        // Update data every 30 seconds
        updateSensorData();
        updateWateringStatus();
        updateWeatherForecast();
        
        setInterval(updateSensorData, 30000);
        setInterval(updateWateringStatus, 30000);
        setInterval(updateWeatherForecast, 300000);
    </script>
</body>
</html>
            """)
    
    # Define routes
    @app.route('/')
    def index():
        """Render the dashboard."""
        return render_template('index.html')
    
    @app.route('/api/sensors')
    def get_sensors():
        """Get current sensor readings."""
        try:
            # Get latest sensor readings from database
            soil_moisture = system.db.get_latest_sensor_reading('soil_moisture')
            temperature = system.db.get_latest_sensor_reading('temperature')
            humidity = system.db.get_latest_sensor_reading('humidity')
            pressure = system.db.get_latest_sensor_reading('pressure')
            
            # If no readings are available, use default values
            if soil_moisture is None:
                soil_moisture = 0
            if temperature is None:
                temperature = 0
            if humidity is None:
                humidity = 0
            if pressure is None:
                pressure = 0
            
            return jsonify({
                'soil_moisture': round(soil_moisture, 1),
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'pressure': round(pressure, 1)
            })
        except Exception as e:
            logger.error(f"Error getting sensor data: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sensors/history')
    def get_sensor_history():
        """Get sensor reading history."""
        try:
            sensor_type = request.args.get('type', 'soil_moisture')
            limit = int(request.args.get('limit', 100))
            
            # Get sensor readings from database
            readings = system.db.get_sensor_readings(sensor_type, limit=limit)
            
            return jsonify({
                'sensor_type': sensor_type,
                'readings': readings
            })
        except Exception as e:
            logger.error(f"Error getting sensor history: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/watering/status')
    def get_watering_status():
        """Get watering status."""
        try:
            # Get last watering time
            last_watered = system.db.get_last_watering_time()
            
            if last_watered:
                last_watered_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_watered))
            else:
                last_watered_str = "Never"
            
            return jsonify({
                'last_watered': last_watered_str,
                'is_watering': system.watering_system.is_watering
            })
        except Exception as e:
            logger.error(f"Error getting watering status: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/watering/start', methods=['POST'])
    def start_watering():
        """Start watering."""
        try:
            # Check if already watering
            if system.watering_system.is_watering:
                return jsonify({
                    'success': False,
                    'message': 'Watering is already in progress'
                })
            
            # Get current soil moisture
            soil_moisture = system.db.get_latest_sensor_reading('soil_moisture')
            if soil_moisture is None:
                soil_moisture = 0
            
            # Start watering
            duration = system.config['watering']['duration']
            system._start_watering(soil_moisture)
            
            return jsonify({
                'success': True,
                'message': f'Watering started for {duration} seconds'
            })
        except Exception as e:
            logger.error(f"Error starting watering: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/watering/stop', methods=['POST'])
    def stop_watering():
        """Stop watering."""
        try:
            # Check if watering
            if not system.watering_system.is_watering:
                return jsonify({
                    'success': False,
                    'message': 'Watering is not in progress'
                })
            
            # Stop watering
            system.watering_system.stop()
            
            return jsonify({
                'success': True,
                'message': 'Watering stopped'
            })
        except Exception as e:
            logger.error(f"Error stopping watering: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/weather')
    def get_weather():
        """Get weather forecast."""
        try:
            # Get weather forecast
            forecast = system.weather.get_forecast()
            
            return jsonify(forecast)
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/images')
    def get_images():
        """Get list of captured images."""
        try:
            # Get list of images
            image_dir = f"{system.config['system']['data_dir']}/images"
            
            if not os.path.exists(image_dir):
                return jsonify({'images': []})
            
            images = []
            for filename in os.listdir(image_dir):
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    image_path = os.path.join(image_dir, filename)
                    images.append({
                        'filename': filename,
                        'path': image_path,
                        'timestamp': os.path.getmtime(image_path)
                    })
            
            # Sort by timestamp (newest first)
            images.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return jsonify({'images': images})
        except Exception as e:
            logger.error(f"Error getting images: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/images/<path:filename>')
    def get_image(filename):
        """Get a specific image."""
        try:
            image_dir = f"{system.config['system']['data_dir']}/images"
            return send_from_directory(image_dir, filename)
        except Exception as e:
            logger.error(f"Error getting image: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/status')
    def get_system_status():
        """Get system status."""
        try:
            # Get latest sensor readings
            soil_moisture = system.db.get_latest_sensor_reading('soil_moisture')
            temperature = system.db.get_latest_sensor_reading('temperature')
            humidity = system.db.get_latest_sensor_reading('humidity')
            pressure = system.db.get_latest_sensor_reading('pressure')
            
            # Get last watering time
            last_watered = system.db.get_last_watering_time()
            if last_watered:
                last_watered_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_watered))
            else:
                last_watered_str = "Never"
            
            # Get weather forecast
            weather = system.weather.get_forecast()
            weather_summary = weather.get('summary', 'No forecast available')
            
            return jsonify({
                'soil_moisture': soil_moisture,
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure,
                'last_watered': last_watered_str,
                'is_watering': system.watering_system.is_watering,
                'weather_forecast': weather_summary
            })
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app