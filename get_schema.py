import time
import urllib.request
import urllib.error
import json

class GetSchema():
    influx_url = "influxdb:8086"
    influx_db_name = "balena"

    def __init__(self):
        while self.check_api() == False:
            print('Waiting for Influx API')
            time.sleep(5)

    # Check the InfluxDB API is available
    # This is done by checking for a 204 response code on the /ping endpoint
    # Returns boolean true/false
    def check_api(self):
        req = urllib.request.Request('http://' + self.influx_url + '/ping')
        try:
            res = urllib.request.urlopen(req, timeout=5)
            if res.getcode() == 204:
                return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass

        return False

    # Request the schema we need from InfluxDB and return the JSON
    def get_influx_schema(self):
        values = {
            'db' : self.influx_db_name,
            'q' : 'show field keys'
        }

        data = urllib.parse.urlencode(values)
        req = urllib.request.Request('http://' + self.influx_url + '/query?' + data)

        try:
            res = urllib.request.urlopen(req, timeout=5).read()
            data = json.loads(res.decode())
            return data['results'][0]['series']
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError):
            # TODO handle error
            pass

        return False