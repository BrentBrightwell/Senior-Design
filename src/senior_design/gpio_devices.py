import time
import board
import adafruit_ahtx0
import gpiozero

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
temp_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)
temp_humidity_sensor.calibrate

MOTION_SENSOR_PIN = 17
LED_PIN = 13
motion_detected = False
motion_sensor = gpiozero.MotionSensor(MOTION_SENSOR_PIN)
led_array = gpiozero.LED(LED_PIN)

SIREN_PIN = 23
siren = gpiozero.OutputDevice(SIREN_PIN)

def read_temperature_humidity():
    temp_f = temp_humidity_sensor.temperature * 1.8 + 32  # Convert Celsius to Fahrenheit
    humid = temp_humidity_sensor.relative_humidity

    return round(temp_f, 2), round(humid, 2)

def initialize_motion_sensor():
    global motion_detected

    while True:
        motion_sensor.wait_for_motion()
        motion_detected = True
        print("Motion Detected!")
        led_array.on()
        motion_sensor.wait_for_no_motion()
        motion_detected = False
        led_array.off()

def trigger_siren():
    global siren_active
    siren_active = True
    while siren_active:
        siren.on()
        print("Siren ON!")
        time.sleep(1)
    siren.off()

def stop_siren():
    global siren_active
    siren_active = False