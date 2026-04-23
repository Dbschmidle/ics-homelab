import time
import board
import busio
import adafruit_bmp280

# Initialize I2C bus and sensor
i2c = busio.I2C(board.SCL, board.SDA)
bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)  # change to 0x77 if that's what i2cdetect showed

# Optional: set sea-level pressure for more accurate altitude readings
bmp.sea_level_pressure = 1013.25

print("Reading BMP280 — Ctrl+C to stop")
print("-" * 50)

while True:
    temp_c = bmp.temperature
    temp_f = temp_c * 9 / 5 + 32
    pressure = bmp.pressure
    print(f"Temp: {temp_c:.2f} °C / {temp_f:.2f} °F   Pressure: {pressure:.2f} hPa")
    time.sleep(2)



