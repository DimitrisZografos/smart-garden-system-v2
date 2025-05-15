# Hardware Setup Guide

This guide provides detailed instructions for setting up the hardware components of the Smart Garden System with your specific components.

## Your Components List

1. **Raspberry Pi 4 Model B**
2. **Raspberry Pi Camera Module 3**
3. **KeyStudio 0100611 Soil Moisture Sensor**
4. **ADS1015 Analog-to-Digital Converter**
5. **DHT20 Temperature and Humidity Sensor**
6. **Jumper Wires**
7. **Breadboard** (For prototyping)

## Wiring Diagram

### KeyStudio Soil Moisture Sensor with ADS1015

The KeyStudio soil moisture sensor is an analog sensor, so we need to use the ADS1015 ADC to connect it to the Raspberry Pi.

First, connect the ADS1015 to the Raspberry Pi:

```
Raspberry Pi      ADS1015
--------------    -------
3.3V              VDD
GND               GND
GPIO 3 (SCL)      SCL
GPIO 2 (SDA)      SDA
```

Then connect the soil moisture sensor to the ADS1015:

```
ADS1015           Soil Moisture Sensor
-------           -------------------
VDD               VCC
GND               GND
A0                SIG (Signal/Data)
```

### DHT20 Temperature and Humidity Sensor (I2C)

The DHT20 uses I2C communication with four pins: VCC, GND, SCL, and SDA.

```
Raspberry Pi      DHT20 Sensor
--------------    -----------
3.3V              VCC
GND               GND
GPIO 3 (SCL)      SCL
GPIO 2 (SDA)      SDA
```

Note: The DHT20 and ADS1015 both use the same I2C bus (GPIO 2 and 3), which is fine as they have different I2C addresses.

### Raspberry Pi Camera Module 3

1. Locate the Camera Serial Interface (CSI) connector on your Raspberry Pi 4. It's a flat ribbon connector between the HDMI and USB ports.
2. Gently pull up the black plastic clip on the CSI connector.
3. Insert the camera's ribbon cable with the blue side facing the USB ports and the silver connectors facing the HDMI ports.
4. Push down the black plastic clip to secure the ribbon cable.

## Connection Diagram

```
                  +---------------+
                  | Raspberry Pi 4|
                  |               |
+--------+        |               |        +---------+
| Camera |========|CSI Port       |        |  DHT20  |
+--------+        |               |        |  Temp & |
                  |          3.3V |--------| Humidity|
                  |           GND |--------|  Sensor |
                  |           SCL |--------|         |
                  |           SDA |--------|         |
                  |               |        +---------+
                  |               |
                  |               |        +---------+
                  |          3.3V |--------|         |
                  |           GND |--------| ADS1015 |
                  |           SCL |--------|   ADC   |
                  |           SDA |--------|         |
                  |               |        |         |
                  +---------------+        |         |
                                           |         |
                  +-----------------+      |         |
                  | Soil Moisture   |      |         |
                  | Sensor          |------|  A0     |
                  | (KeyStudio)     |      |         |
                  |                 |      |         |
                  +-----------------+      +---------+
```

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

# Install ADS1015 library
sudo pip3 install adafruit-circuitpython-ads1x15

# Install DHT20 library
sudo pip3 install adafruit-circuitpython-ahtx0

# Install camera library
sudo pip3 install picamera2
```

3. **Test Components**:

```bash
# Test I2C connection (check for your devices)
sudo i2cdetect -y 1
# DHT20 should appear at address 0x38
# ADS1015 should appear at address 0x48

# Test camera
libcamera-still -o test.jpg
```

## Calibration

### Soil Moisture Sensor Calibration

1. Place the sensor in completely dry soil (or air) and note the reading
2. Place the sensor in water and note the reading
3. Update the `dry_value` and `wet_value` in `config.yaml`

```yaml
hardware:
  soil_moisture:
    dry_value: 26000  # Replace with your dry reading (example value)
    wet_value: 12000  # Replace with your wet reading (example value)
```

## Step-by-Step Connection Guide

### 1. Prepare Your Raspberry Pi

1. Install Raspberry Pi OS on your SD card
2. Boot up your Raspberry Pi 4
3. Connect to Wi-Fi or Ethernet
4. Update your system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. Enable I2C and Camera interfaces:
   ```bash
   sudo raspi-config
   ```
   Navigate to "Interface Options" → Enable both "Camera" and "I2C"

### 2. Connect the Camera Module 3

1. Ensure the Raspberry Pi is powered off
2. Locate the Camera Serial Interface (CSI) connector
3. Gently pull up the black plastic clip
4. Insert the camera ribbon cable with the blue side facing the USB ports
5. Push down the black plastic clip to secure the cable
6. Test the camera:
   ```bash
   libcamera-still -o test.jpg
   ```

### 3. Connect the ADS1015 ADC

1. Connect the ADS1015 to the breadboard
2. Connect the Raspberry Pi to the ADS1015:
   - Pi 3.3V → ADS1015 VDD
   - Pi GND → ADS1015 GND
   - Pi GPIO 2 (SDA) → ADS1015 SDA
   - Pi GPIO 3 (SCL) → ADS1015 SCL
3. Test the connection:
   ```bash
   sudo i2cdetect -y 1
   ```
   You should see the ADS1015 at address 0x48

### 4. Connect the Soil Moisture Sensor

1. Connect the soil moisture sensor to the breadboard
2. Connect the sensor to the ADS1015:
   - ADS1015 VDD → Soil Moisture VCC
   - ADS1015 GND → Soil Moisture GND
   - ADS1015 A0 → Soil Moisture SIG (Signal)
3. Test the sensor with a simple Python script:
   ```python
   import time
   import board
   import busio
   import adafruit_ads1x15.ads1015 as ADS
   from adafruit_ads1x15.analog_in import AnalogIn

   i2c = busio.I2C(board.SCL, board.SDA)
   ads = ADS.ADS1015(i2c)
   chan = AnalogIn(ads, ADS.P0)

   while True:
       print("Soil Moisture: {:.0f}".format(chan.value))
       time.sleep(1)
   ```

### 5. Connect the DHT20 Temperature/Humidity Sensor

1. Connect the DHT20 to the breadboard
2. Connect the sensor to the Raspberry Pi:
   - Pi 3.3V → DHT20 VCC
   - Pi GND → DHT20 GND
   - Pi GPIO 2 (SDA) → DHT20 SDA
   - Pi GPIO 3 (SCL) → DHT20 SCL
3. Test the sensor with a simple Python script:
   ```python
   import time
   import board
   import adafruit_ahtx0

   i2c = board.I2C()
   sensor = adafruit_ahtx0.AHTx0(i2c)

   while True:
       print("Temperature: {:.1f} C".format(sensor.temperature))
       print("Humidity: {:.1f} %".format(sensor.relative_humidity))
       time.sleep(2)
   ```

## Troubleshooting

### Soil Moisture Sensor Issues

- **No readings**: Check wiring connections and ensure the sensor is powered
- **Inconsistent readings**: Clean the sensor prongs and check for corrosion
- **Always reading the same value**: Verify ADS1015 connections and power

### DHT20 Sensor Issues

- **Sensor not found**: Run `i2cdetect -y 1` to verify the I2C address (should be 0x38)
- **Incorrect readings**: Check for heat sources near the sensor
- **No readings**: Verify wiring and I2C configuration

### ADS1015 Issues

- **Not detected**: Check I2C connections and run `i2cdetect -y 1`
- **Incorrect readings**: Verify power supply is stable (3.3V)
- **No readings**: Check if the correct channel (A0) is being used in code

### Camera Issues

- **No image captured**: Ensure the camera is properly connected to the CSI port
- **Error messages**: Check that the camera is enabled in raspi-config
- **Black images**: Make sure the camera has enough light

## Physical Installation

1. **Sensor Placement**:
   - Place the soil moisture sensor in the soil near the plant roots
   - Position the DHT20 sensor away from direct sunlight
   - Mount the camera with a clear view of the plants

2. **Maintenance**:
   - Clean the soil moisture sensor periodically to prevent mineral buildup
   - Wipe the camera lens to ensure clear images
   - Check all connections regularly

## Running the Smart Garden System

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-garden-university-project.git
   cd smart-garden-university-project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the system:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

4. Access the web interface:
   ```
   http://<raspberry-pi-ip-address>:5000
   ```