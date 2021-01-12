import time
from grafana_dash_gen import GrafanaDashGen
from get_schema import GetSchema
import os

print('Starting dashboard sync, checking APIs...')
grafana_dash_gen = GrafanaDashGen()
get_schema = GetSchema()
print('APIs available, proceeding...')

schema = get_schema.get_influx_schema()
if schema != False:
    for measurement in schema:
        if 'GF_RESET' in os.environ:
            grafana_dash_gen.clear_history(measurement)
            
        grafana_dash_gen.sync_dashboard(measurement)
        grafana_dash_gen.default_dashboard()
    print('Initial dashboard sync complete, have a nice day.')
else:
    print('Initial dashboard sync skipped: No schema found.')

while 1:
    time.sleep(10)
    schema = get_schema.get_influx_schema()
    if schema != False:
        for measurement in schema:
            grafana_dash_gen.sync_dashboard(measurement, quiet = True)
        grafana_dash_gen.default_dashboard()
        print('Interim dashboard sync complete.')
    else:
        print('Interim dashboard sync skipped: No schema found.')
