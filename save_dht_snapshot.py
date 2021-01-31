import json
import sqlite3
import time
from datetime import datetime, timedelta
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        time_now = datetime.now()
        timestamp = int(time_now.timestamp())

        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity

        conn = sqlite3.connect('./sensors.db')
        c = conn.cursor()
        c.execute("INSERT INTO dht_readings VALUES (?, ?, ?, ?)", [timestamp, temperature_f, temperature_c, humidity])
        conn.commit()
        conn.close()

        with open("./dht_readings.json", "w") as write_file:
            json.dump({
                "timestamp": timestamp,
                "humidity": humidity,
                "temp_c": temperature_c,
                "temp_f": temperature_f
            }, write_file)

        break

    except RuntimeError as error:
        print(error.args[0])

    time.sleep(2)
