import json
import sqlite3
import time
from datetime import datetime, timedelta
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
from adafruit_pm25.uart import PM25_UART
import serial

reset_pin = None

uart = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=0.25)
pm25 = PM25_UART(uart, reset_pin)

while True:
    time.sleep(1)

    try:
        aqdata = pm25.read()
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue

    time_now = datetime.now()
    timestamp = int(time_now.timestamp())

    conn = sqlite3.connect('/home/pi/pi_air_sensors/sensors.db')
    c = conn.cursor()
    c.execute("INSERT INTO pm_readings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            timestamp,
            aqdata["pm10 standard"],
            aqdata["pm25 standard"],
            aqdata["pm100 standard"],
            aqdata["pm10 env"],
            aqdata["pm25 env"],
            aqdata["pm100 env"],
            aqdata["particles 03um"],
            aqdata["particles 05um"],
            aqdata["particles 10um"],
            aqdata["particles 25um"],
            aqdata["particles 50um"],
            aqdata["particles 100um"]
    ])
    conn.commit()
    conn.close()

    with open("./pm_readings.json", "w") as write_file:
        json.dump({
            "timestamp": timestamp,
            "pm10_standard": aqdata["pm10 standard"],
            "pm25_standard": aqdata["pm25 standard"],
            "pm100_standard": aqdata["pm100 standard"],
            "pm10_env": aqdata["pm10 env"],
            "pm25_env": aqdata["pm25 env"],
            "pm100_env": aqdata["pm100 env"],
            "particles_03um": aqdata["particles 03um"],
            "particles_05um": aqdata["particles 05um"],
            "particles_10um": aqdata["particles 10um"],
            "particles_25um": aqdata["particles 25um"],
            "particles_50um": aqdata["particles 50um"],
            "particles_100um": aqdata["particles 100um"]
        }, write_file)

    break
