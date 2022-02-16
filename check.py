#!/usr/bin/python3
import config
import json


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


conf = config.Config()


def ds18b20_parse(s):
    # Arduino message @see test/1.ok

    it = '{ "values" : ['
    lines = s.split('---')
    if len(lines) < 2: raise DataError
    if not lines[1].startswith("Sensor"): raise DataError
    if not lines[1].endswith(";"): raise DataError

    sns = lines[1][0:len(lines[1])-1]       # remove last ";"
    sensors = sns.split(';')
    filler = ""
    for sensor in sensors:
        items = sensor.split(':')
        if len(items) != 3: raise DataError  # not Sensor:X:YY.ZZ
        sensor_id(items[0])
        id_value(items[1])
        temp_value(items[2])
        it = it + filler + '{ "id" : "' + items[1] + '", "temp" : ' + items[2] + '}'
        filler = ","
    it = it + ']}'
    return json.loads(it)


def dht22_bmp280_parse(s):
    # Arduino MixedSensor code
    items = s.split(':')
    if len(items) < 9: raise DataError
    if items[1] != "Start": raise DataError
    if items[2] != "Pressure": raise DataError
    pressure_value(items[3])
    if items[4] != "Humidity": raise DataError
    humidity_value(items[5])
    if items[6] != "Temperature": raise DataError
    temp_value(items[7])
    if items[8] != "End": raise DataError

    it = '{ "values" : [' + '{' + '"' + items[2] + '" :' + items[3] + ',' \
         + '"' + items[4] + '" :' + items[5] + ',' \
         + '"' + items[6] + '" :' + items[7] + '}]}'

    return json.loads(it)
