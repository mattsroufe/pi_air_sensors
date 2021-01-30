import sqlite3
import time
from datetime import datetime, timedelta
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity

        time_now = datetime.now()
        timestamp = time_now.timestamp()

        conn = sqlite3.connect('/home/pi/pi_air_sensors/sensors.db')
        c = conn.cursor()
        sql = (
                "INSERT INTO dht_readings VALUES ({},{},{},{})".format(
                int(timestamp), temperature_f, temperature_c, humidity
            )
        )
        c.execute(sql)
        conn.commit()
        conn.close()
        break

    except RuntimeError as error:
        print(error.args[0])

    time.sleep(2)
