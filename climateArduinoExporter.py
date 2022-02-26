#!/usr/bin/python3

from prometheus_client import start_http_server, Gauge
from prometheus_client import CollectorRegistry, push_to_gateway

import datetime, time
import json
import serial
from setup import Config
from check import DataError
from check import ds18b20_parse
from check import dht22bmp280_parse
from check import logmsg
from urllib.error import URLError

conf = Config()

# PUSH and PULL CollectorRegistry are different and can't be mixed ?!?
# If you need both start two instances one for PULL and another for PUSH
registry = CollectorRegistry()  # Used by PUSH, PULL has :default
if conf.CONNECTION == "PUSH":  # Setup and local instance with prometheus PUSHGATEWAY
    climate = Gauge('climate_values', 'Pressure in hPa from bmp280, temp in celsius from DHT22,'

                                      ' humidity in % from bmp280 ', ['id', 'location'], registry=registry)
    temperature = Gauge('temperature_value', 'Temperature readings from ds18b20', ['id', 'location'], registry=registry)
else:
    climate = Gauge('climate_values', 'Pressure in hPa from bmp280, temp in celsius from DHT22,'
                                      ' humidity in % from bmp280 ', ['id', 'location'])
    temperature = Gauge('temperature_value', 'Temperature readings from ds18b20', ['id', 'location'])


def read_serial():
    ser = serial.Serial(conf.DEVICE, conf.READSPEED, timeout=conf.TIMEOUT)
    ser.flushInput()
    ser_bytes = ser.read(conf.BUFFERSIZE)
    return ser_bytes[0:len(ser_bytes) - 2].decode("utf-8")


def read_arduino():
    buff = ''
    try:
        buff = read_serial()
        if conf.PRINTMSG == "Y": logmsg(buff)

        ds18b20_parse(buff, temperature)  # check from ds18b20 and expose as metrics
        dht22bmp280_parse(buff, climate)  # check from dht22bmp280 and expose as metrics

    except UnicodeError:
        logmsg("Error reading arduino'")

    except json.decoder.JSONDecodeError:
        logmsg("Error reading arduino, not connected ?'")

    except serial.serialutil.SerialException:
        logmsg("Error reading arduino, not connected ?'")

    except DataError:
        logmsg(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Error in arduino data, data: ")
        logmsg(buff)


def send_data():
    try:
        push_to_gateway(conf.PUSHGATEWAY, job=conf.PUSHGATEWAY_JOBNAME, registry=registry)
    except URLError as e:
        logmsg("Pushgateway error, code : " + str(e.errno))


if __name__ == '__main__':
    # Start up the prometheus metrics server, see
    # http://<host>:PORT to expose the metrics.
    print('Start climateArduinoExporter listening on port : ' + str(conf.PORT) + ' and arduino ' + conf.DEVICE)
    if conf.CONNECTION != "PUSH": start_http_server(conf.PORT)  # Start a local instance queried by prometheus
    while True:
        read_arduino()
        if conf.CONNECTION == "PUSH": send_data()
        time.sleep(conf.SLEEPSECONDS)  # Sleep seconds ( limit: Data transfer on mobilebroadband, ie.60)
