# Smart Garden System

An intelligent watering and plant monitoring system powered by Raspberry Pi and machine learning.

## Features

- **Automated Watering**: Smart watering based on soil moisture, weather forecast, and plant needs
- **Environmental Monitoring**: Track soil moisture, temperature, humidity, and atmospheric pressure
- **Plant Health Analysis**: Camera-based monitoring with ML for growth tracking and disease detection
- **Weather Integration**: Adjusts watering schedule based on weather forecasts
- **Data Visualization**: Monitor your garden's health through an intuitive dashboard
- **Remote Control**: Manage your garden from anywhere
- **Telegram Notifications**: Get alerts and status updates via Telegram

## Hardware Components

- Raspberry Pi (3B+ or 4)
- Soil Moisture Sensor
- BME280 Sensor (Temperature, Humidity, Pressure)
- Raspberry Pi Camera Module
- Water Pump/Solenoid Valve
- Relay Module

## Software Architecture

- Python backend for sensor integration and control logic
- SQLite/PostgreSQL database for data storage
- TensorFlow/PyTorch for plant analysis ML models
- Flask web interface with interactive dashboard
- OpenWeatherMap API integration
- Telegram notifications
- Mock implementations for development without hardware

## Installation

### For Development/Demo (No Hardware Required)

```bash
# Clone the repository
git clone https://github.com/YourUsername/smart-garden-system.git
cd smart-garden-system

# Install dependencies
pip install -r requirements.txt

# Run in demo mode (no hardware required)
python run_simple_demo.py
```

### For Production (With Hardware)

```bash
# Clone the repository
git clone https://github.com/YourUsername/smart-garden-system.git
cd smart-garden-system

# Install dependencies
pip install -r requirements.txt

# Install hardware-specific libraries
pip install RPi.GPIO adafruit-circuitpython-bme280 picamera

# Configure your system
python src/setup.py

# Edit config.yaml with your specific settings
# - Set API keys for weather services
# - Configure GPIO pins for your hardware setup
# - Set up Telegram notification settings

# Run the system
python src/main.py
```

## Configuration

Edit the `config.yaml` file to set up your:
- Hardware pins
- Watering thresholds
- Weather API credentials
- Database settings
- Telegram notification settings

## Demo Mode

The system includes a demo mode that simulates sensor readings and system functionality without requiring physical hardware. This is useful for development, testing, and demonstration purposes.

To run in demo mode:

```bash
python run_simple_demo.py
```

This will start a web server with mock data that you can access at http://localhost:12000.

## Required Sensitive Information for Production Use

When deploying this system for real use (not demo mode), you'll need to provide the following sensitive information in your `config.yaml` file:

1. **Weather API Key**: 
   - Sign up for an API key from OpenWeatherMap
   - Add your key to `weather_api.api_key` in config.yaml
   - Location is already set to Volos, Greece

2. **Telegram Bot Token and Chat ID**:
   - Create a Telegram bot using BotFather
   - Add your bot token to `notifications.telegram.bot_token`
   - Add your chat ID to `notifications.telegram.chat_id`

3. **Database Credentials** (if using PostgreSQL):
   - Set `database.user` and `database.password`

4. **Hardware Configuration**:
   - Verify GPIO pin assignments match your physical connections
   - Adjust sensor calibration values as needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.