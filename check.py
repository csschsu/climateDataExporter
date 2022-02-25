#!/usr/bin/python3
import setup
from prometheus_client import Gauge


class DataError(Exception):
    pass


def temp_value(s):
    if len(s) != 5:
        raise DataError
    if s[2] != ".":
        raise DataError
    for char in s:
        if char.isdigit() is False and char != ".":
            raise DataError
    return


def id_value(s):
    if len(s) > 3:
        raise DataError
    for char in s:
        if char.isnumeric() is False:
            raise DataError
    return


def pressure_id(s):
    if not s.startswith("Pressure"):
        raise DataError
    return


def pressure_value(s):
    # 900.00 - 1100.00
    if len(s) < 6 or len(s) > 7:
        raise DataError
    items = s.split('.')
    if len(items[1]) != 2:
        raise DataError
    for char in s:
        if char.isdigit() is False and char != ".":
            raise DataError
    return


def humidity_value(s):
    # 35.00
    if len(s) != 5:
        raise DataError
    if s[2] != ".":
        raise DataError
    for char in s:
        if char.isdigit() is False and char != ".":
            raise DataError
    return


def sensor_id(s):
    if not s == "Sensor":
        raise DataError
    return


def humidity_id(s):
    if not s.startswith("Humidity"):
        raise DataError
    return


def start_id(s):
    if not s.startswith("Start"):
        raise DataError
    return


def end_id(s):
    if not s.endswith("End"):
        raise DataError
    return


conf = setup.Config()


def ds18b20_parse(s, temperature: Gauge):
    # Arduino message #'Locating devices...Found 3 devices.
    # #
    # #---ds18b20:Sensor:1:22.25;Sensor:2:22.37;Sensor:3:22.31;---'

    lines = s.split('---')
    if len(lines) < 2: raise DataError
    if not lines[1].startswith("ds18b20"): return   # not ds18b20 arduino sensor setup
    if not lines[1].endswith(";"): raise DataError
    sensors = lines[1].split(';')
    for idx in range(1, len(sensors)-1):
        items = sensors[idx].split(':')
        if len(items) != 3: raise DataError   # not Sensor:X:YY.ZZ
        sensor_id(items[0])                   # Raise DataError if invalid
        id_value(items[1])                    # Raise DataError if invalid
        temp_value(items[2])                  # Raise DataError if invalid
        temperature.labels(id=items[1], location=conf.LOCATION).set(float(items[2]))  # set metrics
        if conf.PRINTMSG == "Y": print("Export : " + items[1] + ' : ' + items[2])


def dht22bmp280_parse(s, climate: Gauge):
    # Arduino MixedSensor code
    #    BMP280 Sensor event test
    #---:dht22bmp280:Start:Pressure:1003.02:Humidity:31.30:Temperature:24.27:End:---

    lines = s.split('---')
    if len(lines) < 2 : raise DataError
    items = lines[1].split(':')
    if len(items) < 0 : raise DataError
    if items[1] != "dht22bmp280": return   # not dht22_bmp280 arduino sensor setup
    if len(items) < 10: raise DataError
    if items[2] != "Start": raise DataError
    if items[3] != "Pressure": raise DataError
    pressure_value(items[4])
    if items[5] != "Humidity": raise DataError
    humidity_value(items[6])
    if items[7] != "Temperature": raise DataError
    temp_value(items[8])
    if items[9] != "End": raise DataError

    climate.labels(id="Pressure", location=conf.LOCATION).set(float(items[4]))
    climate.labels(id="Humidity", location=conf.LOCATION).set(float(items[6]))
    climate.labels(id="Temperature", location=conf.LOCATION).set(float(items[8]))
    if conf.PRINTMSG == "Y":
        print("Export Pressure: " + items[4] + ' : Humidity: ' + items[6] + ' : Temperature: ' + items[8])
