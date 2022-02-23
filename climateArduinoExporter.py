#!/usr/bin/python3

from prometheus_client import start_http_server, Gauge
import datetime, time
import json
import serial
from setup import Config
from check import DataError
from check import ds18b20_parse
from check import dht22bmp280_parse


climate = Gauge('climate_values', 'Pressure in hPa from bmp280, temp in celsius from DHT22,'
                                  ' humidity in % from bmp280 ', ['id', 'location'])
temperature = Gauge('temperature_value', 'Temperature readings from ds18b20', ['id', 'location'])
conf = Config()


def read_serial():
    ser = serial.Serial(conf.DEVICE, conf.READSPEED, timeout=conf.TIMEOUT)
    ser.flushInput()
    ser_bytes = ser.read(conf.BUFFERSIZE)
    return ser_bytes[0:len(ser_bytes) - 2].decode("utf-8")


def read_arduino():
    buff = ''
    try:
        buff = read_serial()
        if conf.PRINTMSG == "Y": print(buff)

        ds18b20_parse(buff, temperature)   # check if data from ds18b20 is available
        dht22bmp280_parse(buff, climate)  # check if data from dht22_bmp280 is available

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
    # Start up the prometheus metrics server, see
    # http://<host>:PORT to expose the metrics.
    print ('Start climateArduinoExporter listening on port : ' + str(conf.PORT) + ' and arduino ' + conf.DEVICE)
    start_http_server(conf.PORT)
    while True:
        read_arduino()
        time.sleep(20)
