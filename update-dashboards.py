import time
from grafana_dash_gen import GrafanaDashGen
from get_schema import GetSchema
import os

print('Starting dashboard sync, checking APIs...')
grafana_dash_gen = GrafanaDashGen()
get_schema = GetSchema()
print('APIs available, proceeding...')

for measurement in get_schema.get_influx_schema():
    if 'GF_RESET' in os.environ:
        grafana_dash_gen.clear_history(measurement)
        
    grafana_dash_gen.sync_dashboard(measurement)

print('Initial dashboard sync complete, have a nice day.')

while 1:
    time.sleep(10)
    for measurement in get_schema.get_influx_schema():
        grafana_dash_gen.sync_dashboard(measurement, quiet = True)

    print('Interim dashboard sync complete.')
    