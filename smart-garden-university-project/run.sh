#!/bin/bash
# Smart Garden System Startup Script

# Create necessary directories
mkdir -p data
mkdir -p config

# Check if config file exists, create example if not
if [ ! -f config/config.yaml ]; then
    echo "Creating example config file..."
    cat > config/config.yaml << EOF
# Smart Garden System Configuration

# Watering settings
watering:
  moisture_threshold: 30  # Water when moisture is below this percentage
  duration: 10            # Default watering duration in seconds
  cooldown: 60            # Minimum time between watering cycles in minutes
  auto_watering: true     # Enable automatic watering

# Sensor settings
sensors:
  reading_interval: 15    # Sensor reading interval in minutes

# Camera settings
camera:
  enabled: true           # Enable camera
  interval: 6             # Hours between image captures
  resolution: "medium"    # low, medium, high

# Weather settings
weather:
  api_key: ""             # OpenWeatherMap API key
  location: "London"      # Location for weather forecast

# Notification settings
notifications:
  enabled: false          # Enable notifications
  telegram_token: ""      # Telegram bot token
  telegram_chat_id: ""    # Telegram chat ID
EOF
    echo "Example config file created at config/config.yaml"
    echo "Please edit this file with your preferred settings"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip3 install -r requirements.txt

# Start the web interface
echo "Starting Smart Garden System Web Interface..."
cd web_app
python3 app.py &
WEB_PID=$!
cd ..

echo "Web interface started at http://localhost:5000"
echo "You can access it from other devices using http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the system"

# Trap Ctrl+C to kill the web interface
trap "kill $WEB_PID; echo 'Stopping Smart Garden System...'; exit" INT

# Keep the script running
while true; do
    sleep 1
done