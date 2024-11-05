import board
import adafruit_ahtx0

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_ahtx0.AHTx0(i2c)
sensor.calibrate

def read_temperature_humidity():
    temp_f = sensor.temperature * 1.8 + 32  # Convert Celsius to Fahrenheit
    humid = sensor.relative_humidity

    return round(temp_f, 2), round(humid, 2)
