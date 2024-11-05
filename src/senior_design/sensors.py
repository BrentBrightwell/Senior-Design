import board
import adafruit_ahtx0

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_ahtx0.AHTx0(i2c)
sensor.calibrate

def read_temperature_humidity():
    temp = sensor.temperature
    humid = sensor._humidity

    if temp is not None and temp is not None:
        return round(temp, 2), round(humid, 2)
    else:
        print("Failed to retrieve data from sensor, please check connections.")
        return None, None
