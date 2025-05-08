"""
Hardware modules for the Smart Garden System.
"""

from .sensors import SoilMoistureSensor, BME280Sensor, Camera
from .actuators import WateringSystem

__all__ = ['SoilMoistureSensor', 'BME280Sensor', 'Camera', 'WateringSystem']