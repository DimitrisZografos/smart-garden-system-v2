# Hardware Setup Guide

Created by: Dimitris Zografos  
Date: May 2025

This guide provides detailed instructions for setting up the hardware components of the Smart Garden System.

## Components List

- Raspberry Pi (3 or 4 recommended)
- Soil moisture sensor (capacitive or resistive)
- BME280 temperature/humidity/pressure sensor
- Raspberry Pi Camera (required)
- Jumper wires
- Breadboard
- Power supply for Raspberry Pi (5V/2.5A)

## Wiring Diagram

```
Raspberry Pi          Components
-----------          ----------
3.3V      --------- VCC (BME280)
GND       --------- GND (All components)
GPIO 17   --------- Signal (Soil Moisture Sensor)
GPIO 2/SDA -------- SDA (BME280)
GPIO 3/SCL -------- SCL (BME280)
Camera Port ------- Raspberry Pi Camera (required)
```

## Step-by-Step Instructions

### 1. Soil Moisture Sensor Setup

The soil moisture sensor measures the water content in the soil.

**For capacitive soil moisture sensor:**

1. Connect VCC to 3.3V on the Raspberry Pi
2. Connect GND to GND on the Raspberry Pi
3. Connect the signal pin to GPIO 17 on the Raspberry Pi

**Notes:**
- Place the sensor in the soil at a depth of about 2-3 inches
- Keep the electronic part of the sensor above the soil
- For better accuracy, place the sensor away from the edges of the pot

### 2. BME280 Sensor Setup

The BME280 sensor measures temperature, humidity, and barometric pressure.

1. Connect VCC to 3.3V on the Raspberry Pi
2. Connect GND to GND on the Raspberry Pi
3. Connect SCL to GPIO 3 (SCL) on the Raspberry Pi
4. Connect SDA to GPIO 2 (SDA) on the Raspberry Pi

**Notes:**
- The BME280 uses I2C communication
- The default I2C address is 0x76 (some modules use 0x77)
- Place the sensor away from heat sources for accurate readings

### 3. Camera Setup (Required)

1. Locate the camera port on the Raspberry Pi
2. Gently pull up the plastic clip on the port
3. Insert the camera ribbon cable with the blue side facing the Ethernet port
4. Push down the plastic clip to secure the cable

**Notes:**
- Enable the camera in Raspberry Pi configuration (sudo raspi-config)
- Position the camera to capture the plant's growth
- Protect the camera from water and direct sunlight
- The camera is a required component for this project as it's used to monitor plant health and growth

## Testing the Hardware

After connecting all components, you can test each one individually:

1. Test the soil moisture sensor:
   ```
   python sensors.py
   ```

2. Test the BME280 sensor:
   ```
   python sensors.py
   ```

3. Test the water pump:
   ```
   python actuators.py
   ```

4. Test the camera:
   ```
   python sensors.py
   ```

## Troubleshooting

### Soil Moisture Sensor Issues

- **No readings:** Check connections and GPIO pin number
- **Inconsistent readings:** Try calibrating the sensor in dry and wet soil
- **Always reading wet or dry:** Check for short circuits or damaged sensor

### BME280 Sensor Issues

- **I2C errors:** Verify the I2C address (0x76 or 0x77)
- **No readings:** Check connections and enable I2C in Raspberry Pi configuration
- **Inaccurate readings:** Ensure the sensor is away from heat sources

### Output Display

Since this project uses simulated outputs instead of actual hardware control:
- All watering actions will be displayed as messages in the console
- The system will indicate when it would water plants based on sensor readings
- No actual relay or pump is used in this implementation

### Camera Issues

- **No image captured:** Check ribbon cable connection and enable camera in configuration
- **Blurry images:** Adjust the focus ring on the camera
- **Error messages:** Ensure the camera module is properly supported in your OS

## Maintenance Tips

- Regularly check soil moisture sensor for corrosion
- Clean the camera lens periodically for clear images
- Protect outdoor components from weather with appropriate enclosures
- Check all connections periodically for loose wires
- Ensure the camera is properly positioned to capture plant growth