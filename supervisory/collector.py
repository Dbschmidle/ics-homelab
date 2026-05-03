
"""
Modbus-to-InfluxDB collector.

Polls the Pi's Modbus TCP server, decodes BMP280 readings,
and writes them as time-series points to InfluxDB.

Architecture:
  Field zone (Pi)    Supervisory zone (VM)
  ===============    =====================
  BMP280 sensor      collector.py (this script)
       │                     │
       ▼                     ▼
  Modbus server  ───TCP───▶  InfluxDB ◀──── Grafana
"""

import os
import time
import logging
from pymodbus.client import ModbusTcpClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ---------- Configuration ----------
PI_IP = "192.168.0.210"
PI_PORT = 5020
POLL_INTERVAL_SEC = 2

INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "homelab")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "sensors")
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]  # required, no default
# -----------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main():
    log.info(f"Starting collector: {PI_IP}:{PI_PORT} -> {INFLUX_URL} (bucket={INFLUX_BUCKET})")

    modbus = ModbusTcpClient(PI_IP, port=PI_PORT)
    modbus.connect()

    influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    while True:
        try:
            rr = modbus.read_holding_registers(address=0, count=3)
            if rr.isError():
                log.error(f"Modbus read error: {rr}")
            else:
                temp_c = rr.registers[0] / 100.0
                pressure_hpa = rr.registers[1] / 10.0
                counter = rr.registers[2]

                point = (
                    Point("environment")
                    .tag("device", "raspberry-pi")
                    .tag("zone", "field")
                    .field("temperature_c", temp_c)
                    .field("pressure_hpa", pressure_hpa)
                    .field("counter", counter)
                )
                write_api.write(bucket=INFLUX_BUCKET, record=point)
                log.info(f"Wrote: temp={temp_c:.2f}C pressure={pressure_hpa:.2f}hPa counter={counter}")

        except Exception as e:
            log.error(f"Polling cycle failed: {e}")

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()



