#!/bin/bash
# Smart Garden System Startup Script

# Create necessary directories
mkdir -p data
mkdir -p config

# Create a simple config file if it doesn't exist
if [ ! -f config/config.yaml ]; then
    echo "Creating config file..."
    cat > config/config.yaml << EOF
# Smart Garden System Configuration
watering:
  moisture_threshold: 30
  duration: 10
weather:
  api_key: ""
  location: "London"
camera:
  interval: 6
  rotation: 0
EOF
    echo "Config file created at config/config.yaml"
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Start the web interface
echo "Starting Smart Garden System..."
cd web_app
python3 app.py &
WEB_PID=$!

echo "Web interface started at http://localhost:5000"
echo "Access from other devices: http://$(hostname -I | awk '{print $1}'):5000"
echo "Press Ctrl+C to stop"

# Handle Ctrl+C to stop the system
trap "kill $WEB_PID; echo 'Stopping Smart Garden System'; exit" INT

# Keep the script running
while true; do
    sleep 1
done