"""
Smart Garden System - Sensor Module
Created by: Dimitris Zografos
Date: May 2025

This module handles all sensor interactions for the Smart Garden System.
It provides functions to read data from soil moisture sensors, BME280 
temperature/humidity/pressure sensors, and the camera.
"""

import time
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('sensors')

# Try to import hardware-specific libraries
# These might not be available if not running on a Raspberry Pi
try:
    import RPi.GPIO as GPIO
    import board
    import busio
    import adafruit_bme280.advanced as adafruit_bme280
    from picamera import PiCamera
    HARDWARE_AVAILABLE = True
except ImportError:
    logger.warning("Hardware libraries not available. Running in simulation mode.")
    HARDWARE_AVAILABLE = False

# Note: Camera is a required component for this project
# Even in simulation mode, we'll create simulated camera functionality

class SensorManager:
    """
    Manages all sensors in the Smart Garden System.
    
    This class provides methods to initialize sensors, read their values,
    and store the data for later analysis.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the sensor manager with the provided configuration.
        
        Args:
            config: Dictionary containing sensor configuration from config.yaml
        """
        self.config = config
        self.hardware_config = config.get('hardware', {})
        self.data_config = config.get('data', {})
        self.storage_path = self.data_config.get('storage_path', './data')
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            logger.info(f"Created data storage directory: {self.storage_path}")
        
        # Initialize sensors if hardware is available
        if HARDWARE_AVAILABLE:
            self._setup_gpio()
            self._setup_bme280()
            self._setup_camera()
        else:
            logger.info("Hardware not available. Sensors will return simulated values.")
    
    def _setup_gpio(self) -> None:
        """Set up GPIO pins for soil moisture sensor."""
        try:
            # Set up GPIO for soil moisture sensor
            GPIO.setmode(GPIO.BCM)
            soil_pin = self.hardware_config.get('soil_moisture', {}).get('pin', 17)
            GPIO.setup(soil_pin, GPIO.IN)
            logger.info(f"Soil moisture sensor initialized on pin {soil_pin}")
        except Exception as e:
            logger.error(f"Failed to set up GPIO: {str(e)}")
            raise
    
    def _setup_bme280(self) -> None:
        """Set up BME280 temperature/humidity/pressure sensor."""
        bme_config = self.hardware_config.get('bme280', {})
        if not bme_config.get('enabled', True):
            logger.info("BME280 sensor disabled in configuration")
            self.bme280 = None
            return
            
        try:
            # Create I2C interface
            i2c = busio.I2C(board.SCL, board.SDA)
            # Create BME280 instance
            address = bme_config.get('i2c_address', 0x76)
            self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
            
            # Configure the sensor for higher accuracy
            self.bme280.sea_level_pressure = 1013.25  # Standard sea level pressure in hPa
            self.bme280.standby_period = adafruit_bme280.STANDBY_TC_500
            self.bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
            
            logger.info(f"BME280 sensor initialized at address 0x{address:x}")
        except Exception as e:
            logger.error(f"Failed to initialize BME280 sensor: {str(e)}")
            self.bme280 = None
    
    def _setup_camera(self) -> None:
        """Set up Raspberry Pi camera."""
        camera_config = self.hardware_config.get('camera', {})
        
        # Camera is a required component for this project
        try:
            self.camera = PiCamera()
            resolution = camera_config.get('resolution', [1280, 720])
            self.camera.resolution = (resolution[0], resolution[1])
            self.camera.rotation = camera_config.get('rotation', 0)
            # Warm up the camera
            self.camera.start_preview()
            time.sleep(2)  # Camera warm-up time
            self.camera.stop_preview()
            logger.info(f"Camera initialized with resolution {resolution}")
        except Exception as e:
            logger.warning(f"Failed to initialize physical camera: {str(e)}")
            logger.info("Using simulated camera functionality instead")
            self.camera = None
    
    def read_soil_moisture(self) -> int:
        """
        Read the soil moisture level.
        
        Returns:
            Soil moisture percentage (0-100, where 0 is dry and 100 is wet)
        """
        if not HARDWARE_AVAILABLE:
            # Return simulated value if hardware is not available
            import random
            return random.randint(20, 80)
        
        try:
            # In a real implementation, you would read from an analog sensor
            # This is a simplified example using a digital pin
            soil_pin = self.hardware_config.get('soil_moisture', {}).get('pin', 17)
            
            # Read multiple times and average for stability
            readings = []
            for _ in range(5):
                # This is a placeholder. In reality, you would use ADC to read analog values
                # For a digital sensor, GPIO.input(soil_pin) would return 0 or 1
                # Here we're simulating an analog reading
                reading = GPIO.input(soil_pin)  # 0 = wet, 1 = dry
                readings.append(reading)
                time.sleep(0.1)
            
            # Convert to percentage (0 = dry, 100 = wet)
            # This is a simplified conversion - real sensors would need calibration
            moisture = 100 - (sum(readings) / len(readings) * 100)
            
            logger.debug(f"Soil moisture reading: {moisture:.1f}%")
            return int(moisture)
        except Exception as e:
            logger.error(f"Error reading soil moisture: {str(e)}")
            return -1  # Error value
    
    def read_temperature_humidity(self) -> Tuple[float, float, float]:
        """
        Read temperature, humidity, and pressure from BME280 sensor.
        
        Returns:
            Tuple of (temperature in °C, humidity in %, pressure in hPa)
        """
        if not HARDWARE_AVAILABLE or self.bme280 is None:
            # Return simulated values if hardware is not available
            import random
            return (
                round(random.uniform(18.0, 28.0), 1),  # Temperature
                round(random.uniform(30.0, 70.0), 1),  # Humidity
                round(random.uniform(1000.0, 1020.0), 1)  # Pressure
            )
        
        try:
            # Read from BME280 sensor
            temperature = round(self.bme280.temperature, 1)
            humidity = round(self.bme280.humidity, 1)
            pressure = round(self.bme280.pressure, 1)
            
            logger.debug(f"BME280 readings - Temp: {temperature}°C, Humidity: {humidity}%, Pressure: {pressure}hPa")
            return (temperature, humidity, pressure)
        except Exception as e:
            logger.error(f"Error reading BME280 sensor: {str(e)}")
            return (-1.0, -1.0, -1.0)  # Error values
    
    def capture_image(self, filename: Optional[str] = None) -> str:
        """
        Capture an image from the camera.
        
        Args:
            filename: Optional filename to save the image. If None, a timestamp-based name is used.
            
        Returns:
            Path to the saved image file
        """
        # Generate filename if not provided
        if filename is None:
            filename = os.path.join(self.storage_path, f"plant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        
        if not HARDWARE_AVAILABLE or self.camera is None:
            # Create a simulated image if physical camera is not available
            # This is a required feature, so we always provide an image
            try:
                from PIL import Image, ImageDraw, ImageFont
                import random
                
                # Create a simulated plant image with random color
                img = Image.new('RGB', (640, 480), color=(
                    random.randint(20, 100),  # Darker green for plant
                    random.randint(100, 200),  # More green
                    random.randint(20, 100)   # Less blue
                ))
                
                # Add text with current time and sensor data
                draw = ImageDraw.Draw(img)
                text = f"Plant Image Simulation\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                draw.text((10, 10), text, fill=(255, 255, 255))
                
                # Add some simulated plant features
                for i in range(20):
                    # Draw some leaf-like shapes
                    x = random.randint(50, 590)
                    y = random.randint(50, 430)
                    size = random.randint(20, 60)
                    color = (
                        random.randint(20, 100),
                        random.randint(150, 240),
                        random.randint(20, 100)
                    )
                    draw.ellipse((x, y, x+size, y+size/2), fill=color)
                
                # Save the image
                img.save(filename)
                logger.info(f"Saved simulated plant image to {filename}")
                print(f"CAMERA: Captured simulated plant image at {filename}")
                return filename
            except Exception as e:
                logger.error(f"Error creating simulated image: {str(e)}")
                # Create an empty file as fallback
                with open(filename, 'w') as f:
                    f.write("Simulated plant image")
                return filename
        
        try:
            # Capture image with physical camera
            self.camera.capture(filename)
            logger.info(f"Captured real plant image saved to {filename}")
            print(f"CAMERA: Captured real plant image at {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error capturing image: {str(e)}")
            # Create a fallback image
            with open(filename, 'w') as f:
                f.write("Failed to capture plant image")
            return filename
    
    def read_all_sensors(self) -> Dict[str, Any]:
        """
        Read all sensor values and return them as a dictionary.
        
        Returns:
            Dictionary containing all sensor readings
        """
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Read soil moisture
        soil_moisture = self.read_soil_moisture()
        
        # Read temperature, humidity, pressure
        temperature, humidity, pressure = self.read_temperature_humidity()
        
        # Capture image (but don't include in the data dictionary)
        image_path = self.capture_image()
        
        # Create data dictionary
        data = {
            "timestamp": timestamp,
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "image_path": image_path
        }
        
        # Save data to file
        self._save_sensor_data(data)
        
        return data
    
    def _save_sensor_data(self, data: Dict[str, Any]) -> None:
        """
        Save sensor data to a JSON file.
        
        Args:
            data: Dictionary containing sensor readings
        """
        try:
            # Create filename based on date
            date_str = datetime.now().strftime('%Y%m%d')
            filename = os.path.join(self.storage_path, f"sensor_data_{date_str}.json")
            
            # Load existing data if file exists
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    try:
                        file_data = json.load(f)
                        if not isinstance(file_data, list):
                            file_data = []
                    except json.JSONDecodeError:
                        file_data = []
            else:
                file_data = []
            
            # Append new data
            file_data.append(data)
            
            # Save updated data
            with open(filename, 'w') as f:
                json.dump(file_data, f, indent=2)
            
            logger.debug(f"Saved sensor data to {filename}")
        except Exception as e:
            logger.error(f"Error saving sensor data: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        if HARDWARE_AVAILABLE:
            # Clean up GPIO
            GPIO.cleanup()
            
            # Clean up camera
            if self.camera is not None:
                self.camera.close()
            
            logger.info("Sensor resources cleaned up")


# Example usage if this file is run directly
if __name__ == "__main__":
    import yaml
    
    # Load configuration
    try:
        with open("config/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        config = {}
    
    # Create sensor manager
    sensor_manager = SensorManager(config)
    
    # Read all sensors
    print("Reading sensors...")
    data = sensor_manager.read_all_sensors()
    
    # Print results
    print("\nSensor Readings:")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Soil Moisture: {data['soil_moisture']}%")
    print(f"Temperature: {data['temperature']}°C")
    print(f"Humidity: {data['humidity']}%")
    print(f"Pressure: {data['pressure']} hPa")
    print(f"Image saved to: {data['image_path']}")
    
    # Clean up
    sensor_manager.cleanup()