# Hardware Setup Guide

This guide provides detailed instructions for setting up the hardware components of the Smart Garden System.

## Components List

1. **Raspberry Pi** (3B+ or 4 recommended)
2. **Soil Moisture Sensor** (Capacitive or resistive)
3. **BME280 Sensor** (Temperature, humidity, pressure)
4. **Raspberry Pi Camera Module**
5. **Water Pump** (5V or 12V DC pump)
6. **Relay Module** (1-channel or more)
7. **Power Supply** (For Raspberry Pi and pump)
8. **Jumper Wires**
9. **Breadboard** (For prototyping)
10. **Tubing** (For water delivery)
11. **Enclosure** (Optional, for weather protection)

## Wiring Diagram

### Soil Moisture Sensor

The soil moisture sensor typically has three pins: VCC, GND, and DATA.

```
Raspberry Pi      Soil Moisture Sensor
--------------    -------------------
5V                VCC
GND               GND
GPIO 17           DATA
```

### BME280 Sensor (I2C)

The BME280 sensor uses I2C communication with four pins: VCC, GND, SCL, and SDA.

```
Raspberry Pi      BME280 Sensor
--------------    ------------
3.3V              VCC
GND               GND
GPIO 3 (SCL)      SCL
GPIO 2 (SDA)      SDA
```

### Relay Module (for Water Pump)

The relay module typically has three pins: VCC, GND, and IN.

```
Raspberry Pi      Relay Module
--------------    ------------
5V                VCC
GND               GND
GPIO 18           IN
```

Connect the water pump to the relay's normally open (NO) terminal and power supply.

```
Power Supply      Relay Module      Water Pump
------------      ------------      ----------
Positive (+)      COM               -
-                 -                 -
-                 NO                Positive (+)
Negative (-)      -                 Negative (-)
```

### Camera Module

Connect the camera module to the Raspberry Pi's CSI (Camera Serial Interface) port.

## Software Setup

1. **Enable I2C and Camera**:

```bash
sudo raspi-config
```

Navigate to "Interfacing Options" and enable both I2C and Camera.

2. **Install Required Libraries**:

```bash
# Update package list
sudo apt-get update

# Install I2C tools
sudo apt-get install -y python3-smbus i2c-tools

# Install GPIO library
sudo pip3 install RPi.GPIO

# Install BME280 library
sudo pip3 install adafruit-circuitpython-bme280

# Install camera library
sudo pip3 install picamera
```

3. **Test Components**:

```bash
# Test I2C connection (BME280 usually appears at address 0x76 or 0x77)
sudo i2cdetect -y 1

# Test GPIO (for soil moisture sensor and relay)
# Use the provided test scripts in the repository
python3 tests/test_soil_moisture.py
python3 tests/test_relay.py

# Test camera
python3 tests/test_camera.py
```

## Calibration

### Soil Moisture Sensor Calibration

1. Place the sensor in completely dry soil (or air) and note the reading
2. Place the sensor in water and note the reading
3. Update the `dry_value` and `wet_value` in `config.yaml`

```yaml
hardware:
  soil_moisture:
    dry_value: 800  # Replace with your dry reading
    wet_value: 300  # Replace with your wet reading
```

## Troubleshooting

### Soil Moisture Sensor Issues

- **No readings**: Check wiring connections and ensure the sensor is powered
- **Inconsistent readings**: Clean the sensor prongs and check for corrosion
- **Always reading wet/dry**: Verify calibration values in config.yaml

### Relay/Pump Issues

- **Relay clicks but pump doesn't run**: Check pump power connections
- **Pump runs continuously**: Check GPIO configuration and relay wiring
- **Relay doesn't click**: Verify GPIO pin number and relay power

### BME280 Issues

- **Sensor not found**: Run `i2cdetect -y 1` to verify the I2C address
- **Incorrect readings**: Check for heat sources near the sensor
- **No readings**: Verify wiring and I2C configuration

### Camera Issues

- **No image captured**: Ensure the camera is properly connected to the CSI port
- **Blurry images**: Adjust the focus ring on the camera module
- **Error messages**: Check that the camera is enabled in raspi-config

## Physical Installation

1. **Sensor Placement**:
   - Place the soil moisture sensor in the soil near the plant roots
   - Position the BME280 sensor away from direct sunlight
   - Mount the camera with a clear view of the plants

2. **Water Delivery**:
   - Position the water pump in a water reservoir
   - Run tubing from the pump to the base of the plants
   - Consider using a drip irrigation system for efficient water delivery

3. **Enclosure**:
   - Place the Raspberry Pi and electronics in a waterproof enclosure
   - Ensure proper ventilation to prevent overheating
   - Use waterproof connectors for outdoor installations

## Maintenance

1. **Regular Cleaning**:
   - Clean the soil moisture sensor periodically to prevent mineral buildup
   - Wipe the camera lens to ensure clear images
   - Check and clean the water pump and tubing

2. **System Checks**:
   - Periodically verify sensor readings against known values
   - Check water flow and pump operation
   - Inspect wiring for damage or corrosion

## Extending the System

### Adding Multiple Sensors

To monitor multiple plants or zones, you can add additional soil moisture sensors:

1. Connect each sensor to a different GPIO pin
2. Update the configuration in `config.yaml`
3. Modify the code to handle multiple sensors

### Adding a Water Level Sensor

To monitor the water reservoir level:

1. Connect a float switch or ultrasonic distance sensor
2. Add the appropriate code to read the sensor
3. Configure alerts for low water levels

### Adding Solar Power

For outdoor installations without power access:

1. Connect a solar panel and charge controller
2. Add a battery for energy storage
3. Configure the system for low-power operation