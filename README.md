# Smart Garden System (University Project)

A simple automated plant monitoring system using Raspberry Pi with simulated outputs.

Created by: Dimitris Zografos  
Date: May 2025

## Overview

This project creates an automated plant monitoring system that uses sensors to track soil moisture, temperature, humidity, and pressure. It makes intelligent watering decisions based on sensor readings and weather forecasts, displays what actions would be taken (without controlling actual hardware), and sends notifications via Telegram.

## Features

- **Soil Moisture Monitoring**: Detects when plants need water
- **Simulated Watering**: Displays messages about watering decisions (no actual hardware control)
- **Weather Integration**: Checks weather forecasts to avoid watering when rain is expected
- **Temperature & Humidity Monitoring**: Tracks environmental conditions
- **Telegram Notifications**: Sends alerts about system status and decisions
- **Image Capture**: Takes photos of plants to monitor growth (required feature)
- **Data Logging**: Stores sensor readings and system events for analysis

## Hardware Requirements

- Raspberry Pi (3 or 4 recommended)
- Soil moisture sensor
- BME280 temperature/humidity/pressure sensor
- Raspberry Pi Camera (required)
- Jumper wires and breadboard

## Software Requirements

- Python 3.7+
- Required Python packages (see requirements.txt)
- Telegram bot token (for notifications)
- OpenWeatherMap API key (for weather forecasts)

## Installation

1. Clone this repository to your Raspberry Pi:
   ```
   git clone https://github.com/DimitrisZografos/smart-garden-system.git
   cd smart-garden-system
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Copy the example configuration file and edit it:
   ```
   cp config/config.yaml.example config/config.yaml
   nano config/config.yaml
   ```

4. Set up your Telegram bot:
   - Create a new bot using BotFather on Telegram
   - Add the bot token to your config.yaml
   - Start a conversation with your bot
   - Get your chat ID and add it to config.yaml

5. Get an OpenWeatherMap API key:
   - Sign up at https://openweathermap.org/
   - Create an API key
   - Add the API key to your config.yaml

## Hardware Setup

### Soil Moisture Sensor
- Connect VCC to 3.3V
- Connect GND to ground
- Connect signal pin to GPIO 17 (or as configured)

### BME280 Sensor
- Connect VCC to 3.3V
- Connect GND to ground
- Connect SCL to GPIO 3 (SCL)
- Connect SDA to GPIO 2 (SDA)

### Camera (Required)
- Connect the Raspberry Pi Camera to the camera port
- Enable camera in Raspberry Pi configuration
- Position to capture plant growth

## Usage

Run the main application:
```
python smart_garden.py
```

The system will:
1. Read sensor data at regular intervals
2. Check soil moisture levels
3. Display messages about watering decisions (considering weather forecast)
4. Capture images of plants to monitor growth
5. Send notifications about system events
6. Store data for analysis

## Configuration Options

Edit `config/config.yaml` to customize:

- Sensor pins and thresholds
- Watering duration
- Check interval
- Weather location
- Notification settings

## Troubleshooting

### Sensor Readings Not Working
- Check wiring connections
- Verify GPIO pin numbers in config.yaml
- Run `python sensors.py` to test sensors independently

### Watering Simulation Not Working
- Check configuration settings
- Verify soil moisture thresholds in config.yaml
- Run `python actuators.py` to test the simulation independently

### Weather Data Not Updating
- Check your API key in config.yaml
- Verify internet connection
- Run `python weather.py` to test weather API

### Notifications Not Working
- Verify Telegram bot token and chat ID
- Ensure you've started a conversation with your bot
- Run `python notifications.py` to test notifications

## Future Improvements

- [ ] Web interface for remote monitoring and control
- [ ] Multiple zone support for different plants
- [ ] Machine learning for optimized watering schedules
- [ ] Plant recognition using camera images
- [ ] Growth tracking and analysis from captured images

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenWeatherMap for weather data
- Adafruit for BME280 library
- Python-Telegram-Bot for Telegram integration