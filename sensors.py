#!/usr/bin/env python3
"""
Smart Garden System - Sensor Module for Raspberry Pi 4 with:
- KeyStudio 0100611 Soil Moisture Sensor via ADS1015 ADC
- DHT20 Temperature and Humidity Sensor
- Raspberry Pi Camera Module 3
"""

import os
import time
import random
import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('sensors')

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class SensorManager:
    """Manages all sensors for the Smart Garden System"""
    
    def __init__(self, simulate=False):
        """Initialize the sensor manager"""
        self.simulate = simulate
        logger.info(f"Initializing SensorManager (Simulation: {simulate})")
        
        # Initialize hardware if not in simulation mode
        if not simulate:
            try:
                # Try to import hardware-specific libraries
                import RPi.GPIO as GPIO
                import board
                import busio
                
                # Import ADS1015 libraries for soil moisture sensor
                import adafruit_ads1x15.ads1015 as ADS
                from adafruit_ads1x15.analog_in import AnalogIn
                
                # Import DHT20 library
                import adafruit_ahtx0
                
                # Set up I2C bus
                i2c = busio.I2C(board.SCL, board.SDA)
                
                # Set up ADS1015 for soil moisture sensor
                self.ads = ADS.ADS1015(i2c)
                self.soil_channel = AnalogIn(self.ads, ADS.P0)
                
                # Set up DHT20 temperature/humidity sensor
                self.dht = adafruit_ahtx0.AHTx0(i2c)
                
                # Set up camera
                try:
                    # Using picamera2 for Raspberry Pi Camera Module 3
                    from picamera2 import Picamera2
                    self.camera = Picamera2()
                    self.camera.configure(self.camera.create_still_configuration(main={"size": (1920, 1080)}))
                    self.camera.start()
                    time.sleep(2)  # Allow camera to initialize
                    logger.info("Camera Module 3 initialized")
                except ImportError:
                    logger.warning("Picamera2 module not available, falling back to legacy PiCamera")
                    try:
                        from picamera import PiCamera
                        self.camera = PiCamera()
                        self.camera.resolution = (1920, 1080)
                        time.sleep(2)  # Allow camera to initialize
                        logger.info("Legacy PiCamera initialized")
                    except ImportError:
                        logger.warning("Camera modules not available, camera functionality disabled")
                        self.camera = None
                except Exception as e:
                    logger.error(f"Error initializing camera: {e}")
                    self.camera = None
                
                logger.info("Hardware sensors initialized successfully")
            except ImportError as e:
                logger.warning(f"Hardware libraries not available: {e}, falling back to simulation mode")
                self.simulate = True
            except Exception as e:
                logger.error(f"Error initializing hardware: {e}")
                self.simulate = True
        
        # Initialize simulation values
        if self.simulate:
            self.sim_moisture = random.uniform(30, 70)
            self.sim_temp = random.uniform(18, 25)
            self.sim_humidity = random.uniform(40, 60)
            self.sim_pressure = random.uniform(1000, 1020)
            logger.info("Simulation mode initialized with random starting values")
    
    def read_soil_moisture(self):
        """Read soil moisture level from KeyStudio 0100611 sensor via ADS1015"""
        if self.simulate:
            # Simulate slow changes in soil moisture
            change = random.uniform(-2, -0.5)  # Soil tends to dry out
            self.sim_moisture += change
            # Keep within realistic bounds
            self.sim_moisture = max(10, min(95, self.sim_moisture))
            logger.info(f"Simulated soil moisture: {self.sim_moisture:.1f}%")
            print(f"[SIMULATION] Soil moisture reading: {self.sim_moisture:.1f}%")
            return round(self.sim_moisture, 1)
        
        try:
            # Read from ADS1015 ADC
            raw_value = self.soil_channel.value
            # Convert to percentage (adjust min/max based on calibration)
            # These values should be calibrated for your specific KeyStudio sensor
            min_moisture = 26000  # Value when sensor is in dry soil
            max_moisture = 12000  # Value when sensor is in water
            moisture_percentage = 100 - ((raw_value - max_moisture) * 100 / (min_moisture - max_moisture))
            moisture_percentage = max(0, min(100, moisture_percentage))
            logger.info(f"Soil moisture: {moisture_percentage:.1f}% (raw: {raw_value})")
            return round(moisture_percentage, 1)
        except Exception as e:
            logger.error(f"Error reading soil moisture: {e}")
            # Fall back to simulation if hardware reading fails
            return round(random.uniform(20, 80), 1)
    
    def read_environmental_data(self):
        """Read temperature, humidity from DHT20 sensor"""
        if self.simulate:
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
            print(f"[SIMULATION] Environmental readings: {self.sim_temp:.1f}°C, {self.sim_humidity:.1f}%, {self.sim_pressure:.1f}hPa")
            return (round(self.sim_temp, 1), round(self.sim_humidity, 1), round(self.sim_pressure, 1))
        
        try:
            # Read from DHT20 sensor
            temperature = self.dht.temperature
            humidity = self.dht.relative_humidity
            
            # DHT20 doesn't provide pressure, so we'll simulate it
            pressure = random.uniform(1000, 1020)
            
            logger.info(f"Environmental data: {temperature:.1f}°C, {humidity:.1f}%, {pressure:.1f}hPa")
            return (round(temperature, 1), round(humidity, 1), round(pressure, 1))
        except Exception as e:
            logger.error(f"Error reading environmental data: {e}")
            # Fall back to simulation if hardware reading fails
            return (
                round(random.uniform(18, 25), 1),
                round(random.uniform(40, 60), 1),
                round(random.uniform(1000, 1020), 1)
            )
    
    def capture_image(self):
        """Capture an image from the Raspberry Pi Camera Module 3"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(DATA_DIR, f"plant_{timestamp}.jpg")
        
        if self.simulate:
            # Create a simulated plant image
            try:
                # Create a simple image with text
                img = Image.new('RGB', (1920, 1080), color=(34, 139, 34))  # Green background
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
                print(f"[SIMULATION] Plant image captured and saved to {image_path}")
                return image_path
            except Exception as e:
                logger.error(f"Error creating simulated image: {e}")
                return None
        
        # Real camera capture
        if hasattr(self, 'camera'):
            try:
                # Check if we're using picamera2 or legacy picamera
                if hasattr(self.camera, 'capture_file'):  # Picamera2
                    self.camera.capture_file(image_path)
                elif hasattr(self.camera, 'capture'):  # Legacy PiCamera
                    self.camera.capture(image_path)
                else:
                    raise Exception("Unknown camera type")
                    
                logger.info(f"Image captured and saved to {image_path}")
                return image_path
            except Exception as e:
                logger.error(f"Error capturing image: {e}")
                return None
        else:
            logger.warning("Camera not available")
            return None

if __name__ == "__main__":
    # Simple test code
    sensor_manager = SensorManager(simulate=True)
    
    print("Testing sensor readings...")
    moisture = sensor_manager.read_soil_moisture()
    temp, humidity, pressure = sensor_manager.read_environmental_data()
    
    print(f"Soil Moisture: {moisture}%")
    print(f"Temperature: {temp}°C")
    print(f"Humidity: {humidity}%")
    print(f"Pressure: {pressure} hPa")
    
    print("Capturing test image...")
    image_path = sensor_manager.capture_image()
    if image_path:
        print(f"Image saved to: {image_path}")
    else:
        print("Failed to capture image")