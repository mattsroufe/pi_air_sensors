#!/usr/bin/python3

from flask import Flask
from flask import render_template
import json
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT22(board.D4)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data.json')
def data():
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        return json.dumps({"temp_c": temperature_c, "temp_f": temperature_f, "humidity": humidity})

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        return(error.args[0])

@app.route('/js/index.js')
def bundle():
    return render_template('/js/index.js')

