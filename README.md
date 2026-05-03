# ICS Home Lab

A miniature industrial control system simulating a field-to-supervisory data
pipeline using real hardware and industry-standard protocols.

## Components

**Field device (Raspberry Pi 3B+)**
- BMP280 sensor (temperature + barometric pressure) over I2C
- Custom Modbus TCP server exposing readings as holding registers
- Runs as a systemd service for resilience and auto-restart

**Modbus register map**
| Register | Field         | Encoding              | Example  |
|----------|---------------|-----------------------|----------|
| HR0      | Temperature   | int16 × 100 (°C)      | 2547 = 25.47°C |
| HR1      | Pressure      | int16 × 10 (hPa)      | 9989 = 998.9 hPa |
| HR2      | Counter       | int16, increments     | Liveness indicator |

**Supervisory VM (Debian on Proxmox)**
- `collector.py` — polls field device over Modbus TCP, writes to InfluxDB
- InfluxDB 2.x — time-series storage for historical data
- Grafana — web HMI with live charts, trends, and alarming

## Repo layout
ics-homelab/
├── field-device/
│   ├── modbus_server.py      # Modbus TCP server (runs on Pi)
│   ├── bmp280_read.py        # Standalone sensor reader for testing
│   ├── requirements.txt
│   └── systemd/
│       └── modbus-server.service
├── supervisory/
│   ├── collector.py          # Modbus → InfluxDB writer (runs on VM)
│   ├── poll.py               # Standalone Modbus client for testing
│   └── requirements.txt
└── README.md

## Field device setup (Raspberry Pi)

1. Wire the BMP280 to the Pi's GPIO header:
   - VIN → Pin 1 (3.3V)
   - GND → Pin 6 (GND)
   - SDA / SDI → Pin 3 (GPIO 2)
   - SCL / SCK → Pin 5 (GPIO 3)
2. Enable I2C: `sudo raspi-config` → Interface Options → I2C → Enable
3. Verify the sensor: `i2cdetect -y 1` should show `0x77`
4. Clone this repo and set up Python:
```bash
   git clone https://github.com/Dbschmidle/ics-homelab.git
   cd ics-homelab
   python3 -m venv venv && source venv/bin/activate
   pip install -r field-device/requirements.txt
```
5. Install the Modbus server as a systemd service:
```bash
   sudo cp field-device/systemd/modbus-server.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now modbus-server.service
   sudo systemctl status modbus-server.service
```

## Supervisory setup (Debian VM on Proxmox)

1. Install InfluxDB 2.x and Grafana from their official repos
2. Configure InfluxDB: create org, bucket (`sensors`), and an API token
3. Clone this repo and set up Python:
```bash
   git clone https://github.com/Dbschmidle/ics-homelab.git
   cd ics-homelab
   python3 -m venv venv && source venv/bin/activate
   pip install -r supervisory/requirements.txt
```
4. Run the collector with InfluxDB credentials:
```bash
   export INFLUX_TOKEN="your-token-here"
   export INFLUX_ORG="homelab"
   export INFLUX_BUCKET="sensors"
   python supervisory/collector.py
```
5. In Grafana, add InfluxDB as a data source and build a dashboard with
   panels querying the `environment` measurement for `temperature_c`
   and `pressure_hpa` fields.

<img width="1907" height="953" alt="image" src="https://github.com/user-attachments/assets/ddaa84e2-c279-4ac7-a884-dfb98aa413be" />



Granfana Alerting -> Personal Email
<img width="1907" height="953" alt="image" src="https://github.com/user-attachments/assets/bbedfe9b-f328-40e1-8988-7a2eaa256c13" />


Example Alert
<img width="1589" height="753" alt="image" src="https://github.com/user-attachments/assets/5ad92ec6-248c-4647-9c88-d55c5389126a" />


## What's next
- [ ] VLAN-based network segmentation between field and supervisory zones,
      following IEC-62443 zone-and-conduit principles
- [ ] DNP3 as a second protocol for utility-grade comparison



