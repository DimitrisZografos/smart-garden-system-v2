#!/usr/bin/env python3
"""
Hardware Test Script for Smart Garden System

This script tests each hardware component individually:
1. ADS1015 ADC with KeyStudio 0100611 Soil Moisture Sensor
2. DHT20 Temperature and Humidity Sensor
3. Raspberry Pi Camera Module 3

Run this script after connecting all components to verify they're working correctly.
"""

import time
import os
import sys

def test_i2c_devices():
    """Test I2C devices (ADS1015 and DHT20)"""
    print("\n=== Testing I2C Devices ===")
    try:
        import board
        import busio
        
        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Scan for I2C devices
        print("Scanning for I2C devices...")
        devices_found = []
        
        # Scan all possible I2C addresses
        for address in range(0x00, 0x80):
            try:
                i2c.writeto(address, b'')
                devices_found.append(address)
            except:
                pass
        
        if not devices_found:
            print("No I2C devices found!")
            return False
        
        print(f"Found {len(devices_found)} I2C devices at addresses:")
        for address in devices_found:
            device_name = ""
            if address == 0x48:
                device_name = "ADS1015 ADC"
            elif address == 0x38:
                device_name = "DHT20 Sensor"
            
            print(f"  0x{address:02X} {device_name}")
        
        # Check for our specific devices
        if 0x48 in devices_found:
            print("✓ ADS1015 ADC detected")
        else:
            print("✗ ADS1015 ADC not found! Check connections.")
        
        if 0x38 in devices_found:
            print("✓ DHT20 sensor detected")
        else:
            print("✗ DHT20 sensor not found! Check connections.")
            
        return 0x48 in devices_found and 0x38 in devices_found
    
    except ImportError as e:
        print(f"Error importing required libraries: {e}")
        print("Make sure you've installed the required packages:")
        print("  pip install adafruit-blinka adafruit-circuitpython-ads1x15 adafruit-circuitpython-ahtx0")
        return False
    except Exception as e:
        print(f"Error testing I2C devices: {e}")
        return False

def test_soil_moisture_sensor():
    """Test the soil moisture sensor via ADS1015"""
    print("\n=== Testing Soil Moisture Sensor ===")
    try:
        import board
        import busio
        import adafruit_ads1x15.ads1015 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn
        
        # Initialize I2C and ADS1015
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1015(i2c)
        
        # Connect soil moisture sensor to A0
        soil_channel = AnalogIn(ads, ADS.P0)
        
        # Read values
        print("Reading soil moisture sensor...")
        print("Place sensor in dry soil (or air) and then in wet soil (or water).")
        print("Press Ctrl+C to stop the test.")
        
        try:
            while True:
                raw_value = soil_channel.value
                voltage = soil_channel.voltage
                
                # Convert to percentage (example calibration)
                min_moisture = 26000  # Value when sensor is in dry soil
                max_moisture = 12000  # Value when sensor is in water
                moisture_percentage = 100 - ((raw_value - max_moisture) * 100 / (min_moisture - max_moisture))
                moisture_percentage = max(0, min(100, moisture_percentage))
                
                print(f"Raw Value: {raw_value}, Voltage: {voltage:.2f}V, Moisture: {moisture_percentage:.1f}%")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nSoil moisture sensor test stopped.")
        
        return True
    
    except ImportError as e:
        print(f"Error importing required libraries: {e}")
        print("Make sure you've installed the required packages:")
        print("  pip install adafruit-blinka adafruit-circuitpython-ads1x15")
        return False
    except Exception as e:
        print(f"Error testing soil moisture sensor: {e}")
        return False

def test_dht20_sensor():
    """Test the DHT20 temperature and humidity sensor"""
    print("\n=== Testing DHT20 Temperature and Humidity Sensor ===")
    try:
        import board
        import adafruit_ahtx0
        
        # Initialize I2C and DHT20
        i2c = board.I2C()
        sensor = adafruit_ahtx0.AHTx0(i2c)
        
        # Read values
        print("Reading DHT20 sensor...")
        print("Press Ctrl+C to stop the test.")
        
        try:
            while True:
                temperature = sensor.temperature
                humidity = sensor.relative_humidity
                
                print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nDHT20 sensor test stopped.")
        
        return True
    
    except ImportError as e:
        print(f"Error importing required libraries: {e}")
        print("Make sure you've installed the required packages:")
        print("  pip install adafruit-blinka adafruit-circuitpython-ahtx0")
        return False
    except Exception as e:
        print(f"Error testing DHT20 sensor: {e}")
        return False

def test_camera():
    """Test the Raspberry Pi Camera Module 3"""
    print("\n=== Testing Raspberry Pi Camera Module 3 ===")
    try:
        # First try picamera2 (for newer Raspberry Pi OS)
        try:
            from picamera2 import Picamera2
            
            print("Initializing Camera Module 3 with picamera2...")
            camera = Picamera2()
            camera.configure(camera.create_still_configuration(main={"size": (1920, 1080)}))
            camera.start()
            time.sleep(2)  # Allow camera to initialize
            
            # Capture an image
            test_image_path = "camera_test.jpg"
            print(f"Capturing test image to {test_image_path}...")
            camera.capture_file(test_image_path)
            
            if os.path.exists(test_image_path):
                print(f"✓ Camera test successful! Image saved to {test_image_path}")
                return True
            else:
                print("✗ Failed to save image!")
                return False
                
        except ImportError:
            # Fall back to legacy picamera
            print("picamera2 not available, trying legacy picamera...")
            from picamera import PiCamera
            
            print("Initializing Camera Module with legacy picamera...")
            camera = PiCamera()
            camera.resolution = (1920, 1080)
            time.sleep(2)  # Allow camera to initialize
            
            # Capture an image
            test_image_path = "camera_test.jpg"
            print(f"Capturing test image to {test_image_path}...")
            camera.capture(test_image_path)
            
            if os.path.exists(test_image_path):
                print(f"✓ Camera test successful! Image saved to {test_image_path}")
                return True
            else:
                print("✗ Failed to save image!")
                return False
    
    except ImportError as e:
        print(f"Error importing camera libraries: {e}")
        print("Make sure you've installed the required packages:")
        print("  pip install picamera2")
        print("  or")
        print("  pip install picamera")
        return False
    except Exception as e:
        print(f"Error testing camera: {e}")
        print("Make sure the camera is properly connected and enabled in raspi-config")
        return False

def main():
    """Run all hardware tests"""
    print("=== Smart Garden System Hardware Test ===")
    print("This script will test all hardware components.")
    print("Make sure all components are properly connected.")
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        if 'Raspberry Pi' not in cpuinfo:
            print("Warning: This doesn't appear to be a Raspberry Pi.")
            print("Hardware tests may not work correctly.")
    except:
        print("Warning: Unable to determine if this is a Raspberry Pi.")
    
    # Run tests
    i2c_ok = test_i2c_devices()
    
    if i2c_ok:
        input("\nPress Enter to test the soil moisture sensor...")
        soil_ok = test_soil_moisture_sensor()
        
        input("\nPress Enter to test the DHT20 sensor...")
        dht_ok = test_dht20_sensor()
    else:
        print("\nSkipping sensor tests due to I2C issues.")
        soil_ok = False
        dht_ok = False
    
    input("\nPress Enter to test the camera...")
    camera_ok = test_camera()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"I2C Devices: {'✓ OK' if i2c_ok else '✗ Failed'}")
    print(f"Soil Moisture Sensor: {'✓ OK' if soil_ok else '✗ Failed'}")
    print(f"DHT20 Sensor: {'✓ OK' if dht_ok else '✗ Failed'}")
    print(f"Camera: {'✓ OK' if camera_ok else '✗ Failed'}")
    
    if i2c_ok and soil_ok and dht_ok and camera_ok:
        print("\nAll hardware tests passed! Your system is ready to use.")
    else:
        print("\nSome tests failed. Please check the connections and try again.")

if __name__ == "__main__":
    main()