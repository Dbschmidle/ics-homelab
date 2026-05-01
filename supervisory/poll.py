"""Quick test: read 3 holding registers from the Pi and decode them."""
import time
from pymodbus.client import ModbusTcpClient

PI_IP = "127.0.0.1"  # localhost for now - change to your Pi's actual IP
PI_PORT = 5020

client = ModbusTcpClient(PI_IP, port=PI_PORT)
client.connect()

while True:
    rr = client.read_holding_registers(address=0, count=3)
    if rr.isError():
        print(f"Error: {rr}")
    else:
        temp = rr.registers[0] / 100
        pressure = rr.registers[1] / 10
        counter = rr.registers[2]
        print(f"Temp: {temp:.2f}°C  Pressure: {pressure:.2f} hPa  Counter: {counter}")
    time.sleep(2)


