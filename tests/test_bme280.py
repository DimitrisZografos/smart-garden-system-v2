#!/usr/bin/env python3
"""
Test script for BME280 sensor.
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hardware.sensors import BME280Sensor

def main():
    """Test the BME280 sensor."""
    print('Testing BME280 Sensor')
    print('===================')

    # Create sensor instance
    sensor = BME280Sensor(i2c_address='0x76')

    # Read sensor data
    data = sensor.read()
    print('\nSensor readings:')
    print(f'Temperature: {data.get("temperature", "N/A")} °C')
    print(f'Humidity: {data.get("humidity", "N/A")} %')
    print(f'Pressure: {data.get("pressure", "N/A")} hPa')

    print('\nTest completed')

if __name__ == '__main__':
    main()
