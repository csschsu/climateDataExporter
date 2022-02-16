#!/usr/bin/python3

from prometheus_client import start_http_server, Gauge
import datetime, time
import serial
import json
from config import Config
from check import DataError
from check import ds18b20_parse
from check import dht22_bmp280_parse

temperature = Gauge('temperature_value', 'Temperature readings from ds18b20', ['id'])
conf = Config()

def read_serial():
    ser = serial.Serial(conf.DEVICE, conf.READSPEED, timeout=conf.TIMEOUT)
    ser.flushInput()
    ser_bytes = ser.read(conf.BUFFERSIZE)
    return ser_bytes[0:len(ser_bytes) - 2].decode("utf-8")

def read_arduino():
    try:

        buff = read_serial()
        if conf.PRINTMSG == "Y": print(buff)

        if conf.SENSOR == "ds18b20":
            values = ds18b20_parse(buff)
        elif conf.SENSOR == "dht22_bmp280":
            values = dht22_bmp280_parse(buff) # TODO not fully supported yet
        else:
            buff = "unknown sensor"
            raise DataError

        for value in values["values"]:
            identity = 'id' + value['id']
            val = float(value['temp'])
            temperature.labels(id=identity).set(val) # set metrics


    except UnicodeError:
        print("Error reading arduino'")

    except json.decoder.JSONDecodeError:
        print("Error reading arduino, not connected ?'")

    except serial.serialutil.SerialException:
        print("Error reading arduino, not connected ?'")

    except DataError:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Error in arduino data, data: ")
        print(buff)


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(7991)
    while True:
        read_arduino()
        time.sleep(10)
