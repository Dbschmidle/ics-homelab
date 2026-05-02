## Field device setup

1. Clone the repo on the Pi.
2. Install Python dependencies: `pip install -r field-device/requirements.txt`
3. Wire BMP280 to Pi GPIO (pin 1 → VIN, pin 6 → GND, pin 3 → SDA, pin 5 → SCL).
4. Install the Modbus server as a systemd service:
