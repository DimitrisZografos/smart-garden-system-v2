#!/usr/bin/env python3
"""
Smart Garden System - Main Module
This is the main entry point for the Smart Garden System.
It coordinates all components and implements the main control logic.

The system monitors soil moisture and environmental conditions,
waters plants when needed, and captures images of the plants.
"""

import os
import time
import yaml
import logging
import threading
import datetime
import schedule
import json
from sensors import SensorManager
from actuators import WateringSystem
from weather import WeatherForecast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("garden_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# Constants
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Ensure directories exist
for directory in [CONFIG_DIR, DATA_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

class SmartGardenSystem:
    """Main class for the Smart Garden System"""
    
    def __init__(self, config_file='config.yaml', simulate=False):
        """
        Initialize the Smart Garden System
        
        Args:
            config_file (str): Path to the configuration file
            simulate (bool): If True, use simulation mode
        """
        self.simulate = simulate
        logger.info(f"Initializing Smart Garden System (Simulation: {simulate})")
        
        # Load configuration
        self.config_path = os.path.join(CONFIG_DIR, config_file)
        self.config = self.load_config()
        
        # Initialize components
        self.sensor_manager = SensorManager(simulate=simulate)
        self.watering_system = WateringSystem(
            relay_pin=self.config.get('watering', {}).get('relay_pin', 17),
            simulate=simulate
        )
        
        # Initialize weather forecast if API key is provided
        weather_config = self.config.get('weather', {})
        self.weather_forecast = None
        if 'api_key' in weather_config:
            self.weather_forecast = WeatherForecast(
                api_key=weather_config.get('api_key'),
                location=weather_config.get('location', 'London')
            )
        
        # Initialize state variables
        self.last_watered = None
        self.last_image = None
        self.running = False
        self.latest_data = {
            'soil_moisture': 0,
            'temperature': 0,
            'humidity': 0,
            'pressure': 0,
            'last_watered': 'Never',
            'watering_status': 'Idle',
            'weather_forecast': 'Unknown',
            'last_updated': datetime.datetime.now().isoformat()
        }
        
        # Set up schedules
        self.setup_schedules()
    
    def load_config(self):
        """
        Load configuration from file
        
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            'watering': {
                'moisture_threshold': 30,  # Water when below this percentage
                'duration': 10,  # Watering duration in seconds
                'cooldown': 60,  # Minimum time between waterings in minutes
                'relay_pin': 17  # GPIO pin for relay
            },
            'sensors': {
                'reading_interval': 15  # Sensor reading interval in minutes
            },
            'camera': {
                'enabled': True,
                'interval': 6  # Hours between images
            },
            'weather': {
                'location': 'London'
            },
            'notifications': {
                'enabled': False
            }
        }
        
        # Create default config if it doesn't exist
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            logger.info(f"Created default configuration at {self.config_path}")
            return default_config
        
        # Load existing config
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            return default_config
    
    def setup_schedules(self):
        """Set up scheduled tasks"""
        # Clear existing schedules
        schedule.clear()
        
        # Schedule sensor readings
        reading_interval = self.config.get('sensors', {}).get('reading_interval', 15)
        schedule.every(reading_interval).minutes.do(self.check_conditions)
        
        # Schedule camera captures
        if self.config.get('camera', {}).get('enabled', True):
            camera_interval = self.config.get('camera', {}).get('interval', 6)
            schedule.every(camera_interval).hours.do(self.capture_plant_image)
        
        # Schedule weather updates
        if self.weather_forecast:
            schedule.every(1).hours.do(self.update_weather)
        
        logger.info("Schedules set up")
    
    def start(self):
        """Start the system"""
        if self.running:
            logger.warning("System already running")
            return
        
        self.running = True
        logger.info("Starting Smart Garden System")
        
        # Initial readings
        self.check_conditions()
        if self.config.get('camera', {}).get('enabled', True):
            self.capture_plant_image()
        if self.weather_forecast:
            self.update_weather()
        
        # Main loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("System stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.stop()
    
    def stop(self):
        """Stop the system"""
        self.running = False
        logger.info("Stopping Smart Garden System")
        
        # Clean up
        if self.watering_system:
            self.watering_system.cleanup()
    
    def check_conditions(self):
        """Check sensor readings and water if needed"""
        logger.info("Checking conditions")
        
        try:
            # Read sensors
            soil_moisture = self.sensor_manager.read_soil_moisture()
            temperature, humidity, pressure = self.sensor_manager.read_environmental_data()
            
            # Update latest data
            self.latest_data['soil_moisture'] = soil_moisture
            self.latest_data['temperature'] = temperature
            self.latest_data['humidity'] = humidity
            self.latest_data['pressure'] = pressure
            self.latest_data['last_updated'] = datetime.datetime.now().isoformat()
            
            # Save data
            self.save_data()
            
            # Check if watering is needed
            self.check_watering(soil_moisture)
            
            return soil_moisture, temperature, humidity, pressure
        except Exception as e:
            logger.error(f"Error checking conditions: {e}")
            return None
    
    def check_watering(self, soil_moisture):
        """
        Check if watering is needed and water if necessary
        
        Args:
            soil_moisture (float): Current soil moisture percentage
        """
        # Get watering configuration
        moisture_threshold = self.config.get('watering', {}).get('moisture_threshold', 30)
        watering_duration = self.config.get('watering', {}).get('duration', 10)
        cooldown_minutes = self.config.get('watering', {}).get('cooldown', 60)
        
        # Check if soil is dry enough to need watering
        if soil_moisture < moisture_threshold:
            logger.info(f"Soil moisture ({soil_moisture}%) below threshold ({moisture_threshold}%)")
            
            # Check cooldown period
            if self.last_watered is None or (datetime.datetime.now() - self.last_watered).total_seconds() > cooldown_minutes * 60:
                logger.info(f"Watering plants for {watering_duration} seconds")
                
                # Update status before watering
                self.latest_data['watering_status'] = f"Watering for {watering_duration}s"
                self.save_data()
                
                # Water plants
                self.watering_system.water_plants(duration=watering_duration)
                self.last_watered = datetime.datetime.now()
                
                # Update status after watering
                self.latest_data['last_watered'] = self.last_watered.isoformat()
                self.latest_data['watering_status'] = 'Idle'
                self.save_data()
                
                # Capture image after watering if enabled
                if self.config.get('camera', {}).get('enabled', True):
                    # Wait a bit for water to soak in
                    time.sleep(30)
                    self.capture_plant_image()
            else:
                cooldown_remaining = cooldown_minutes - (datetime.datetime.now() - self.last_watered).total_seconds() / 60
                logger.info(f"Watering needed but in cooldown period ({cooldown_remaining:.1f} minutes remaining)")
        else:
            logger.info(f"Soil moisture ({soil_moisture}%) above threshold ({moisture_threshold}%), no watering needed")
    
    def capture_plant_image(self):
        """Capture an image of the plants"""
        logger.info("Capturing plant image")
        
        try:
            image_path = self.sensor_manager.capture_image()
            if image_path:
                self.last_image = image_path
                logger.info(f"Image captured: {image_path}")
            else:
                logger.warning("Failed to capture image")
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
    
    def update_weather(self):
        """Update weather forecast"""
        if not self.weather_forecast:
            return
        
        logger.info("Updating weather forecast")
        
        try:
            forecast = self.weather_forecast.get_forecast()
            if forecast:
                self.latest_data['weather_forecast'] = forecast
                self.save_data()
                logger.info(f"Weather forecast updated: {forecast}")
            else:
                logger.warning("Failed to update weather forecast")
        except Exception as e:
            logger.error(f"Error updating weather forecast: {e}")
    
    def save_data(self):
        """Save the latest data to a file"""
        data_file = os.path.join(DATA_DIR, 'latest_data.json')
        try:
            with open(data_file, 'w') as f:
                json.dump(self.latest_data, f)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
        
        # Also append to history file
        history_file = os.path.join(DATA_DIR, 'data_history.json')
        try:
            history_data = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r') as f:
                        history_data = json.load(f)
                except:
                    history_data = []
            
            # Add timestamp to current data
            current_data = self.latest_data.copy()
            current_data['timestamp'] = datetime.datetime.now().isoformat()
            
            # Limit history to 1000 entries
            history_data.append(current_data)
            if len(history_data) > 1000:
                history_data = history_data[-1000:]
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f)
        except Exception as e:
            logger.error(f"Error saving history data: {e}")

if __name__ == "__main__":
    # Check if we should use simulation mode
    import argparse
    parser = argparse.ArgumentParser(description='Smart Garden System')
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode')
    args = parser.parse_args()
    
    # Create and start the system
    garden_system = SmartGardenSystem(simulate=args.simulate)
    garden_system.start()