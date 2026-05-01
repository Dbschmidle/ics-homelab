"""
Modbus TCP server exposing BMP280 sensor readings as holding registers.

Register map (holding registers, 16-bit unsigned):
  HR0: temperature in centi-degrees Celsius (e.g., 2547 = 25.47 C)
  HR1: pressure in deci-hectopascals (e.g., 9989 = 998.9 hPa)
  HR2: rolling counter (increments each update)
"""

import asyncio
import logging

import board
import busio
import adafruit_bmp280

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ---------- Real BMP280 sensor over I2C ----------
i2c = busio.I2C(board.SCL, board.SDA)
bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
bmp.sea_level_pressure = 1013.25
# -------------------------------------------------

hr_block = ModbusSequentialDataBlock(0, [0] * 100)
slave_context = ModbusSlaveContext(hr=hr_block)
server_context = ModbusServerContext(slaves=slave_context, single=True)


async def update_registers(period_seconds: float = 2.0):
    """Continuously read the sensor and update the Modbus holding registers."""
    counter = 0
    while True:
        try:
            temp_c = bmp.temperature
            pressure_hpa = bmp.pressure

            temp_register = int(round(temp_c * 100)) & 0xFFFF
            pressure_register = int(round(pressure_hpa * 10)) & 0xFFFF
            counter = (counter + 1) & 0xFFFF

            slave_context.setValues(3, 0, [temp_register, pressure_register, counter])
            log.info(f"Updated: temp={temp_c:.2f}C pressure={pressure_hpa:.2f}hPa counter={counter}")

        except Exception as e:
            log.error(f"Sensor read failed: {e}")

        await asyncio.sleep(period_seconds)


async def main():
    log.info("Starting Modbus TCP server on 0.0.0.0:5020")
    log.info("Holding registers: HR0=temp*100, HR1=pressure*10, HR2=counter")
    update_task = asyncio.create_task(update_registers())
    await StartAsyncTcpServer(context=server_context, address=("0.0.0.0", 5020))
    update_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())


