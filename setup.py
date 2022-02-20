import json


class Config:

    TESTDATA: object

    def __init__(self):
        with open("setup.json") as json_data_file:
            data = json.load(json_data_file)
            self.PORT = data["PORT"]                # this API endpoint
            self.DEVICE = data["DEVICE"]            # arduino device ie /dev/ttyACM0 ( uno ), /dev/ttyUSB0 (nano)
            self.LOCATION = data["LOCATION"]        # kök
            self.SENSOR = data["SENSOR"]            # one of ds18b20 or dht22_bmp280
            self.BUFFERSIZE = data["BUFFERSIZE"]    # 200 bytes per read
            self.READSPEED = data["READSPEED"]      # 9600 (baud)
            self.TIMEOUT = data["TIMEOUT"]          # 5 (seconds)
            self.TESTDIR = data["TESTDIR"]          # Directory for test files
            self.PRINTMSG = data["PRINTMSG"]        # Y/N
