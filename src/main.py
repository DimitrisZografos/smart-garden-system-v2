"""
Main application for the Smart Garden System.
"""

import os
import sys
import time
import logging
import yaml
import schedule
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware.sensors import SoilMoistureSensor, BME280Sensor, Camera
from src.hardware.actuators import WateringSystem
from src.database_manager import DatabaseManager
from src.weather_api import WeatherAPI
from src.notification_manager import NotificationManager
from src.ml.plant_analyzer import PlantAnalyzer
from src.web_interface import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/garden.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

class SmartGardenSystem:
    """
    Main class for the Smart Garden System.
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the Smart Garden System.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Create data and log directories if they don't exist
        os.makedirs(self.config['system']['data_dir'], exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Set up components
        self._setup_components()
        
        # Schedule tasks
        self._schedule_tasks()
        
        logger.info("Smart Garden System initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load the configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The configuration as a dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            sys.exit(1)
    
    def _setup_components(self) -> None:
        """Set up the system components."""
        try:
            # Initialize hardware
            self.soil_sensor = SoilMoistureSensor(
                pin=self.config['hardware']['soil_moisture']['pin'],
                dry_value=self.config['hardware']['soil_moisture']['dry_value'],
                wet_value=self.config['hardware']['soil_moisture']['wet_value']
            )
            
            self.bme280 = BME280Sensor(
                i2c_address=self.config['hardware']['bme280']['i2c_address']
            )
            
            self.watering_system = WateringSystem(
                pin=self.config['hardware']['pump']['pin'],
                active_low=self.config['hardware']['pump']['active_low']
            )
            
            if self.config['hardware']['camera']['enabled']:
                self.camera = Camera(
                    resolution=tuple(self.config['hardware']['camera']['resolution'])
                )
            else:
                self.camera = None
            
            # Initialize database
            self.db = DatabaseManager(self.config['database'])
            
            # Initialize weather API
            self.weather = WeatherAPI(self.config['weather_api'])
            
            # Initialize notification manager
            self.notifications = NotificationManager(self.config['notifications'])
            
            # Initialize ML component
            if self.config['ml']['enabled']:
                self.plant_analyzer = PlantAnalyzer(self.config['ml'])
            else:
                self.plant_analyzer = None
            
            # Initialize web interface
            if self.config['web_interface']['enabled']:
                self.app = create_app(self)
            else:
                self.app = None
                
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up components: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to initialize system: {str(e)}", 
                "System Initialization"
            )
            raise
    
    def _schedule_tasks(self) -> None:
        """Schedule recurring tasks."""
        # Schedule sensor readings
        schedule.every(self.config['hardware']['soil_moisture']['read_interval']).seconds.do(
            self.read_soil_moisture
        )
        
        schedule.every(self.config['hardware']['bme280']['read_interval']).seconds.do(
            self.read_environmental_data
        )
        
        # Schedule camera capture if enabled
        if self.camera and self.config['hardware']['camera']['enabled']:
            schedule.every(self.config['hardware']['camera']['capture_interval']).seconds.do(
                self.capture_image
            )
        
        # Schedule weather updates
        schedule.every(self.config['weather_api']['update_interval']).seconds.do(
            self.update_weather
        )
        
        # Schedule system status notification
        schedule.every(12).hours.do(self.send_status_update)
        
        # Schedule ML model training if enabled
        if self.plant_analyzer and self.config['ml']['enabled']:
            schedule.every(self.config['ml']['training_interval']).seconds.do(
                self.train_ml_model
            )
        
        logger.info("Tasks scheduled")
    
    def read_soil_moisture(self) -> float:
        """
        Read the soil moisture level.
        
        Returns:
            The soil moisture percentage
        """
        try:
            moisture = self.soil_sensor.read_percentage()
            logger.info(f"Soil moisture: {moisture:.1f}%")
            
            # Store in database
            self.db.store_sensor_reading('soil_moisture', moisture)
            
            # Check if watering is needed
            self._check_watering_needed(moisture)
            
            # Check if alert is needed
            if moisture < self.config['notifications']['alerts']['low_moisture']:
                self.notifications.send_sensor_alert(
                    "Soil Moisture", moisture, 
                    self.config['notifications']['alerts']['low_moisture'], "%"
                )
            
            return moisture
            
        except Exception as e:
            logger.error(f"Error reading soil moisture: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to read soil moisture: {str(e)}", 
                "Soil Moisture Sensor"
            )
            return -1
    
    def read_environmental_data(self) -> Dict[str, float]:
        """
        Read temperature, humidity, and pressure from the BME280 sensor.
        
        Returns:
            Dictionary with temperature, humidity, and pressure values
        """
        try:
            data = self.bme280.read()
            logger.info(f"Environmental data: {data}")
            
            # Store in database
            for key, value in data.items():
                self.db.store_sensor_reading(key, value)
            
            # Check if temperature alerts are needed
            temp = data.get('temperature', 0)
            if temp > self.config['notifications']['alerts']['high_temperature']:
                self.notifications.send_sensor_alert(
                    "Temperature", temp, 
                    self.config['notifications']['alerts']['high_temperature'], "°C"
                )
            elif temp < self.config['notifications']['alerts']['low_temperature']:
                self.notifications.send_sensor_alert(
                    "Temperature", temp, 
                    self.config['notifications']['alerts']['low_temperature'], "°C"
                )
            
            return data
            
        except Exception as e:
            logger.error(f"Error reading environmental data: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to read environmental data: {str(e)}", 
                "BME280 Sensor"
            )
            return {}
    
    def capture_image(self) -> str:
        """
        Capture an image from the camera.
        
        Returns:
            Path to the captured image
        """
        if not self.camera:
            logger.warning("Camera capture requested but camera is not enabled")
            return ""
            
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_path = f"{self.config['system']['data_dir']}/images/{timestamp}.jpg"
            
            # Ensure the directory exists
            os.makedirs(f"{self.config['system']['data_dir']}/images", exist_ok=True)
            
            # Capture the image
            self.camera.capture(image_path)
            logger.info(f"Image captured: {image_path}")
            
            # Analyze the image if ML is enabled
            if self.plant_analyzer:
                self.plant_analyzer.analyze_image(image_path)
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error capturing image: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to capture image: {str(e)}", 
                "Camera"
            )
            return ""
    
    def update_weather(self) -> Dict[str, Any]:
        """
        Update weather data from the API.
        
        Returns:
            Weather data dictionary
        """
        try:
            weather_data = self.weather.get_forecast()
            logger.info(f"Weather updated: {weather_data.get('summary', 'No summary')}")
            
            # Store in database
            self.db.store_weather_data(weather_data)
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error updating weather: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to update weather: {str(e)}", 
                "Weather API"
            )
            return {}
    
    def _check_watering_needed(self, moisture: float) -> None:
        """
        Check if watering is needed based on soil moisture and weather.
        
        Args:
            moisture: Current soil moisture percentage
        """
        # Get the last watering time
        last_watering = self.db.get_last_watering_time()
        
        # Calculate time since last watering
        if last_watering:
            time_since_watering = time.time() - last_watering
        else:
            time_since_watering = float('inf')  # Never watered before
        
        # Check if we're in the cooldown period
        if time_since_watering < self.config['watering']['cooldown']:
            logger.debug("Still in watering cooldown period")
            return
        
        # Check if moisture is below threshold
        if moisture < self.config['watering']['threshold']:
            # Check weather if weather-aware watering is enabled
            if self.config['watering']['weather_aware']:
                weather_data = self.weather.get_current()
                
                # Skip watering if it's going to rain soon
                if weather_data.get('precipitation_probability', 0) > 70:
                    logger.info("Skipping watering as rain is expected soon")
                    return
            
            # Start watering
            self._start_watering(moisture)
    
    def _start_watering(self, current_moisture: float) -> None:
        """
        Start the watering system.
        
        Args:
            current_moisture: Current soil moisture percentage
        """
        try:
            duration = self.config['watering']['duration']
            logger.info(f"Starting watering for {duration} seconds")
            
            # Send notification
            self.notifications.send_watering_notification(duration, current_moisture)
            
            # Start the pump
            self.watering_system.water(duration)
            
            # Record watering event in database
            self.db.store_watering_event(duration, current_moisture)
            
        except Exception as e:
            logger.error(f"Error during watering: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to water plants: {str(e)}", 
                "Watering System"
            )
    
    def send_status_update(self) -> None:
        """Send a status update notification."""
        try:
            # Get latest sensor readings
            soil_moisture = self.db.get_latest_sensor_reading('soil_moisture')
            temperature = self.db.get_latest_sensor_reading('temperature')
            humidity = self.db.get_latest_sensor_reading('humidity')
            pressure = self.db.get_latest_sensor_reading('pressure')
            
            # Get last watering time
            last_watered = self.db.get_last_watering_time()
            if last_watered:
                last_watered_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_watered))
            else:
                last_watered_str = "Never"
            
            # Get weather forecast
            weather = self.weather.get_forecast()
            weather_summary = weather.get('summary', 'No forecast available')
            
            # Compile status
            status = {
                'soil_moisture': soil_moisture,
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure,
                'last_watered': last_watered_str,
                'weather_forecast': weather_summary
            }
            
            # Send notification
            self.notifications.send_system_status(status)
            
        except Exception as e:
            logger.error(f"Error sending status update: {str(e)}")
    
    def train_ml_model(self) -> None:
        """Train the ML model with new data."""
        if not self.plant_analyzer:
            return
            
        try:
            logger.info("Starting ML model training")
            self.plant_analyzer.train()
            logger.info("ML model training completed")
            
        except Exception as e:
            logger.error(f"Error training ML model: {str(e)}")
            self.notifications.send_error_notification(
                f"Failed to train ML model: {str(e)}", 
                "Plant Analyzer"
            )
    
    def run(self) -> None:
        """Run the main loop of the system."""
        logger.info("Starting Smart Garden System")
        
        # Initial readings
        self.read_soil_moisture()
        self.read_environmental_data()
        self.update_weather()
        
        if self.camera:
            self.capture_image()
        
        # Send initial status update
        self.send_status_update()
        
        # Start web interface if enabled
        if self.app and self.config['web_interface']['enabled']:
            import threading
            
            def run_app():
                self.app.run(
                    host=self.config['web_interface']['host'],
                    port=self.config['web_interface']['port'],
                    debug=self.config['web_interface']['debug']
                )
            
            threading.Thread(target=run_app, daemon=True).start()
            logger.info(f"Web interface started on {self.config['web_interface']['host']}:{self.config['web_interface']['port']}")
        
        # Main loop
        try:
            logger.info("Entering main loop")
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            self.notifications.send_error_notification(
                f"System error: {str(e)}", 
                "Main Loop"
            )
        finally:
            logger.info("Shutting down Smart Garden System")
            # Clean up resources
            if self.watering_system:
                self.watering_system.cleanup()

if __name__ == "__main__":
    system = SmartGardenSystem()
    system.run()