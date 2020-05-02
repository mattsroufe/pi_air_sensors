import sqlite3
from datetime import datetime, timedelta
import board
import serial
import adafruit_dht

dhtDevice = adafruit_dht.DHT22(board.D4)

time_now = datetime.now()
timestamp = time_now.timestamp()
start_time = int((time_now - timedelta(days=1)).replace(second=0).timestamp())

temperature_c = dhtDevice.temperature
temperature_f = temperature_c * (9 / 5) + 32
humidity = dhtDevice.humidity

try:
    import struct
except ImportError:
    import ustruct as struct

uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.25)

buffer = []

while True:
    data = uart.read(32)  # read up to 32 bytes
    data = list(data)
    # print("read: ", data)          # this is a bytearray type

    buffer += data

    while buffer and buffer[0] != 0x42:
        buffer.pop(0)

    if len(buffer) > 200:
        buffer = []  # avoid an overrun if all bad data
    if len(buffer) < 32:
        continue

    if buffer[1] != 0x4d:
        buffer.pop(0)
        continue

    frame_len = struct.unpack(">H", bytes(buffer[2:4]))[0]
    if frame_len != 28:
        buffer = []
        continue

    frame = struct.unpack(">HHHHHHHHHHHHHH", bytes(buffer[4:]))

    pm10_standard, pm25_standard, pm100_standard, pm10_env, \
        pm25_env, pm100_env, particles_03um, particles_05um, particles_10um, \
        particles_25um, particles_50um, particles_100um, skip, checksum = frame

    check = sum(buffer[0:30])

    if check != checksum:
        buffer = []
        continue


    conn = sqlite3.connect('/home/pi/sensors/sensors.db')
    c = conn.cursor()
    sql = (
            "INSERT INTO readings VALUES ({},{:.1f},{:.1f},{},{},{},{},{},{},{},{},{},{},{},{},{})".format(
            int(timestamp), temperature_f, temperature_c, humidity, pm10_standard, pm25_standard, pm100_standard, pm10_env, pm25_env, pm100_env, particles_03um, particles_05um, particles_10um, particles_25um, particles_50um, particles_100um
        )
    )
    c.execute(sql)
    conn.commit()
    f = open("/var/www/html/readings.json", "w")
    for row in c.execute("select json_group_array(json_object('timestamp', timestamp, 'temp_f', temp_f, 'temp_c', temp_c, 'humidity', humidity, 'pm10_standard', pm10_standard, 'pm25_standard', pm25_standard, 'pm100_standard', pm100_standard, 'pm10_env', pm10_env, 'pm25_env', pm25_env, 'pm100_env', pm100_env, 'particles_03um', particles_03um, 'particles_05um', particles_05um, 'particles_10um', particles_10um, 'particles_25um', particles_25um, 'particles_50um', particles_50um, 'particles_100um', particles_100um)) from (select * from readings where timestamp > " + str(start_time) + " order by timestamp)"):
        f.write(''.join(row))
    f.close()
    conn.close()

    break

# print("Concentration Units (standard)")
# print("---------------------------------------")
# print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %
#      (pm10_standard, pm25_standard, pm100_standard))
# print("Concentration Units (environmental)")
# print("---------------------------------------")
# print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm10_env, pm25_env, pm100_env))
# print("---------------------------------------")
# print("Particles > 0.3um / 0.1L air:", particles_03um)
# print("Particles > 0.5um / 0.1L air:", particles_05um)
# print("Particles > 1.0um / 0.1L air:", particles_10um)
# print("Particles > 2.5um / 0.1L air:", particles_25um)
# print("Particles > 5.0um / 0.1L air:", particles_50um)
# print("Particles > 10 um / 0.1L air:", particles_100um)
# print("---------------------------------------")

# buffer = buffer[32:]
# print("Buffer ", buffer)
